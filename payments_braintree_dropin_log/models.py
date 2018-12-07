from django.db import models
from django.conf import settings
from django.apps import apps as django_apps
from django.utils.translation import pgettext_lazy
from django.utils import timezone

from payments import PaymentStatus
from payments.models import PaymentAttributeProxy

currency_kwargs = {}

if getattr(settings, 'AVAILABLE_CURRENCIES', None):
    currency_kwargs['choices'] = [(key, key)
                                  for key in settings.AVAILABLE_CURRENCIES]

if getattr(settings, 'AVAILABLE_CURRENCIES_OVERRIDE', None):
    currency_kwargs['choices'] = settings.AVAILABLE_CURRENCIES_OVERRIDE

if getattr(settings, 'DEFAULT_CURRENCY', None):
    currency_kwargs['default'] = settings.DEFAULT_CURRENCY

if getattr(settings, 'PAYMENTS_BRAINTREE_PAYMENT_MODEL', None):

    class TransactionRecord(models.Model):
        payment = models.ForeignKey(
            settings.PAYMENTS_BRAINTREE_PAYMENT_MODEL,
            on_delete=models.SET_NULL, blank=True, null=True,
            related_name='braintree_transaction_records')
        transaction_id = models.CharField(max_length=255, blank=True)
        created = models.DateTimeField(default=timezone.now)
        status = models.CharField(max_length=10, choices=PaymentStatus.CHOICES,
                                  default=PaymentStatus.WAITING)
        currency = models.CharField(max_length=10, **currency_kwargs)
        primary = models.DecimalField(
            max_digits=9, decimal_places=2, default='0.0')
        tax = models.DecimalField(
            max_digits=9, decimal_places=2, default='0.0')
        delivery = models.DecimalField(
            max_digits=9, decimal_places=2, default='0.0')
        discount = models.DecimalField(
            max_digits=9, decimal_places=2, default='0.0')

        description = models.TextField(blank=True, default='')
        extra_data = models.TextField(blank=True, default='')

        class Meta:
            permissions = (
                ('view', pgettext_lazy('Permission description',
                                       'Can view transaction records')),
                ('edit', pgettext_lazy('Permission description',
                                       'Can edit transaction records')))

        def __str__(self):
            if self.payment and self.transaction_id:
                return '{} - {}'.format(self.transaction_id, self.payment)
            return '{}'.format(self.transaction_id or self.payment)

        @property
        def attrs(self):
            return PaymentAttributeProxy(self)

        @property
        def total(self):
            return self.primary + self.tax + self.delivery + self.discount
