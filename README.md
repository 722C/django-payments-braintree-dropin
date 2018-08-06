# django-payments-braintree-dropin

A [django-payments](https://github.com/mirumee/django-payments) backend for Braintree's Drop-in UI.

There is already a Braintree backend in django-payments, but it doesn't have support for Braintree's Drop-in UI. Using the Drop-in UI allows for easy support for things like:

- Apple Pay support
- Google Pay support
- Venmo support
- PayPal suport
- Stored cards

Documentation about Braintree's Drop-in UI can be found here: https://developers.braintreepayments.com/guides/drop-in/overview/javascript/v3.

## Parameters

- `environment`: The Braintree environment. Options are `sandbox` and `production`.
- `merchant_id`: The merchant id assigned by Braintree.
- `private_key`: The private key assigned by Braintree.
- `public_key`: The public key assigned by Braintree.
- `apple_pay_display_name`: (Optional) The name displayed as the store name in the Apple Pay flow. If this is included, this will enable support in this package for Apple Pay. To use this, you will need to enable [Apple Pay in Braintree](https://developers.braintreepayments.com/guides/apple-pay/configuration/javascript/v3). Further information can be found [here](https://developers.braintreepayments.com/guides/drop-in/setup-and-integration/javascript/v3#apple-pay).
- `google_pay_merchant_id`: (Optional) The Google Pay merchant id. If this is included, this will enable support in this package for Apple Pay. To use this, you will need to enable [Google Pay in Braintree](https://developers.braintreepayments.com/guides/google-pay/configuration/javascript/v3). Further information can be found [here](https://developers.braintreepayments.com/guides/drop-in/setup-and-integration/javascript/v3#google-pay).
- `submit_for_settlement`: (Optional boolean, defaults to `True`) If this value is `True`, then the payment will be submitted for settlement when it was created. If this value is `False`, then the payment will be preauthorized for later capture.

## Usage example

Test configuration using default testing parameters:

```python
PAYMENT_VARIANTS = {
    'braintree_dropin': ('django-payments-braintree-dropin.payments_braintree_dropin.BraintreeDropinProvider', {
        'environment': 'sandbox',  # sandbox or production
        'merchant_id': 'use_your_merchant_id',
        'public_key': 'use_your_public_key',
        'private_key': 'use_your_private_key',
        'apple_pay_display_name': 'apple_pay_store_display_name',  # Optional
        'google_pay_merchant_id': 'google_pay_merchant_id',  # Optional
        'submit_for_settlement': False  # Optional, defaults to True
    }),
}
```
