window.addEventListener('load', function() {
  var inputField = document.getElementById('dropin-container');
  var container = document.createElement('div');
  inputField.insertAdjacentElement('afterend', container);

  var form = inputField.closest('form');

  var braintreeConfiguration = {
    authorization: inputField.dataset.authorization,
    container: container,
  };

  if (inputField.dataset.applepaydisplayname) {
    braintreeConfiguration.applePay = {
      displayName: inputField.dataset.applepaydisplayname,
      paymentRequest: {
        total: {
          label: inputField.dataset.description,
          amount: inputField.dataset.amount,
        },
        // We recommend collecting billing address information, at minimum
        // billing postal code, and passing that billing postal code with all
        // Apple Pay transactions as a best practice.
        requiredBillingContactFields: ['postalAddress'],
      },
    };
  }

  if (inputField.dataset.googlepaymerchantid) {
    braintreeConfiguration.googlePay = {
      merchantId: inputField.dataset.googlepaymerchantid,
      transactionInfo: {
        totalPriceStatus: 'FINAL',
        totalPrice: inputField.dataset.amount,
        currencyCode: inputField.dataset.currency,
      },
      cardRequirements: {
        // We recommend collecting and passing billing address information with all Google Pay transactions as a best practice.
        billingAddressRequired: true,
      },
    };
  }

  braintree.dropin.create(braintreeConfiguration, function(createErr, instance) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      instance.requestPaymentMethod(function(requestPaymentMethodErr, payload) {
        if (!requestPaymentMethodErr) {
          inputField.value = payload.nonce;
          form.submit();
        } else {
          console.error(requestPaymentMethodErr);
        }
      });
    });
  });
});
