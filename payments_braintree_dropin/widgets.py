from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _


class BraintreeDropinWidget(HiddenInput):

    def __init__(self, provider, payment, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        kwargs['attrs'] = {
            'id': 'dropin-container',
            'data-authorization': provider.client_authorization,
            'data-applepaydisplayname': provider.apple_pay_display_name or '',
            'data-googlepaymerchantid': provider.google_pay_merchant_id or '',
            'data-paypalflow': provider.paypal_flow or '',
            'data-description': payment.description or _('Total payment'),
            'data-amount': payment.total,
            'data-currency': payment.currency,
        }
        kwargs['attrs'].update(attrs)
        super(BraintreeDropinWidget, self).__init__(*args, **kwargs)

    class Media:
        js = ['https://js.braintreegateway.com/web/dropin/'
              '1.16.0/js/dropin.min.js',
              'payments-braintree-dropin/dropin.js']
