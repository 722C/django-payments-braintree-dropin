
from django.shortcuts import redirect

from payments import RedirectNeeded
from payments.core import BasicProvider
from .forms import PaymentForm

from braintree import BraintreeGateway, Configuration, Environment


class BraintreeDropinProvider(BasicProvider):

    def __init__(self, *args, **kwargs):
        self.environment = kwargs.pop('environment')
        self.merchant_id = kwargs.pop('merchant_id')
        self.private_key = kwargs.pop('private_key')
        self.public_key = kwargs.pop('public_key')
        self.apple_pay_display_name = kwargs.pop(
            'apple_pay_display_name', '')
        self.google_pay_merchant_id = kwargs.pop(
            'google_pay_merchant_id', '')
        self.submit_for_settlement = kwargs.pop(
            'submit_for_settlement', True)
        self.gateway = BraintreeGateway(
            Configuration(
                (Environment.Sandbox if self.environment ==
                 'sandbox' else Environment.Production),
                merchant_id=self.merchant_id,
                public_key=self.public_key,
                private_key=self.private_key,
            )
        )
        super(BraintreeDropinProvider, self).__init__(*args, **kwargs)

    @property
    def client_authorization(self):

        # Do some magic for Saleor instances that are using it or something
        # with a similar structure.  This allows for effectively free
        # compliant "storing" of cards.  The cards are all stored on
        # Braintree's side.
        if (self.payment and self.payment.order and
                self.payment.order.user):
            customer_id = 'dpbd-{}'.format(
                self.payment.order.user.pk)

            try:
                return self.gateway.client_token.generate({
                    'customer_id': customer_id,
                })
            except ValueError:
                self.gateway.customer.create({
                    'id': customer_id,
                })
                return self.gateway.client_token.generate({
                    'customer_id': customer_id,
                })
        else:
            return self.gateway.client_token.generate()

    def get_form(self, payment, data=None):
        self.payment = payment
        kwargs = {
            'data': data,
            'payment': self.payment,
            'provider': self,
            'action': '',
            'hidden_inputs': False}
        form = PaymentForm(**kwargs)

        if form.is_valid():
            form.save()
            raise RedirectNeeded(self.payment.get_success_url())
        else:
            self.payment.change_status('input')
        return form

    def process_data(self, request):
        if self.payment.status == 'confirmed':
            return redirect(self.payment.get_success_url())
        return redirect(self.payment.get_failure_url())

    def capture(self, payment, amount=None):
        amount = amount or payment.total
        try:
            result = self.gateway.transaction.submit_for_settlement(
                payment.transaction_id, amount)
            payment.attrs.capture = '{}'.format(result.transaction)
            if not result.is_success:
                raise Exception()
        except Exception as e:
            payment.change_status(PaymentStatus.ERROR)
            raise PaymentError('Payment cannot be captured')
        return amount

    def release(self, payment):
        result = self.gateway.transaction.void(payment.transaction_id)
        payment.attrs.release = '{}'.format(result.transaction)

    def refund(self, payment, amount=None):
        amount = amount or payment.total
        result = self.gateway.transaction.refund(
            payment.transaction_id, amount)
        payment.attrs.refund = '{}'.format(result.transaction)
        return amount
