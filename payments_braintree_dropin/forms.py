import json

from django import forms

from payments import PaymentStatus, FraudStatus
from payments.forms import PaymentForm as BasePaymentForm

from ..payments_braintree_dropin_log.utils import (
    log_captured, log_error, log_rejected, log_preauthorized)

from . import RedirectNeeded
from .widgets import BraintreeDropinWidget
from .utils import BRAINTREE_RISK_TO_FRAUD


class PaymentForm(BasePaymentForm):

    charge = None

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        widget = BraintreeDropinWidget(
            provider=self.provider, payment=self.payment)
        self.fields['payment_method_nonce'] = forms.CharField(widget=widget)
        if self.is_bound and not self.data.get('payment_method_nonce'):
            self.payment.change_status('rejected')
            log_rejected(self.payment,
                         self.payment.transaction_id or self.payment.id,
                         'Failed to get payment method nonce.',
                         self.payment.currency, primary=self.payment.total)
            raise RedirectNeeded(self.payment.get_failure_url())

    def clean(self):
        data = self.cleaned_data

        if not self.errors and not self.payment.transaction_id:
            try:
                order_id = self.payment.pk
                if getattr(getattr(self.payment, 'order', None), 'pk', None):
                    order_id = self.payment.order.id
                self.result = self.provider.gateway.transaction.sale({
                    'amount': str(self.payment.total),
                    'payment_method_nonce': data['payment_method_nonce'],
                    'order_id': order_id,
                    'options': {
                        'submit_for_settlement': self.provider.submit_for_settlement,
                    },
                })
                if not self.result.is_success:
                    self.payment.attrs.transaction = '{}\n{}\n{}'.format(
                        json.dumps(self.result.params),
                        self.result.errors.deep_errors,
                        self.result.transaction
                    )
                    self._errors['__all__'] = self.error_class(
                        [self.result.message])
                    self.payment.change_status(PaymentStatus.REJECTED)
                    log_rejected(
                        self.payment,
                        self.payment.transaction_id or self.payment.id,
                        self.result.message,
                        self.payment.currency,
                        primary=self.payment.total,
                        transaction='{}\n{}\n{}'.format(
                            json.dumps(self.result.params),
                            self.result.errors.deep_errors,
                            self.result.transaction,
                        ),
                    )
                else:
                    self.payment.attrs.transaction = '{}'.format(
                        self.result.transaction)
                self.payment.fraud_status = BRAINTREE_RISK_TO_FRAUD.get(
                    getattr(getattr(self.result.transaction,
                                    'risk_data', None), 'decision', None),
                    FraudStatus.UNKNOWN)
                self.payment.save()
            except Exception as e:
                # The card has been declined
                message = getattr(e, 'message', '{}'.format(e))
                self._errors['__all__'] = self.error_class([message])
                self.payment.attrs.error = message
                self.payment.change_status(PaymentStatus.ERROR)
                log_error(
                    self.payment,
                    self.payment.transaction_id or self.payment.id,
                    message, self.payment.currency,
                    primary=self.payment.total,
                    error=message,
                )

        return data

    def save(self):
        self.payment.transaction_id = self.result.transaction.id
        if self.provider.submit_for_settlement:
            self.payment.captured_amount = self.payment.total
            self.payment.change_status(PaymentStatus.CONFIRMED)
            log_captured(self.payment, self.result.transaction.id, '',
                         self.payment.currency, primary=self.payment.total,
                         transaction='{}'.format(self.result.transaction))
        else:
            self.payment.change_status(PaymentStatus.PREAUTH)
            log_preauthorized(self.payment, self.result.transaction.id, '',
                              self.payment.currency, primary=self.payment.total,
                              transaction='{}'.format(self.result.transaction))
