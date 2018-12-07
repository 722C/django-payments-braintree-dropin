import logging

from decimal import Decimal

from django.conf import settings

from payments import PaymentStatus

logger = logging.getLogger(__name__)

TransactionRecord = None

ZERO = Decimal(0)


def log_record(status, payment, transaction_id, description, currency,
               primary=None, tax=None, delivery=None, discount=None,
               **extra_data):
    try:
        global TransactionRecord
        if TransactionRecord is None:
            try:
                from .models import TransactionRecord
            except ImportError:
                TransactionRecord = False

        primary = primary if primary else ZERO
        tax = tax if tax else ZERO
        delivery = delivery if delivery else ZERO
        discount = discount if discount else ZERO

        if TransactionRecord:
            record = TransactionRecord(
                status=status,
                payment=payment, transaction_id=transaction_id,
                currency=currency, primary=primary, tax=tax, delivery=delivery,
                discount=discount, description=description)
            for key, value in extra_data.items():
                setattr(record.attrs, key, value)
            record.save()
    except:
        logger.exception('Failed to record transaction')


def log_preauthorized(*args, **kwargs):
    log_record(PaymentStatus.PREAUTH, *args, **kwargs)


def log_captured(*args, **kwargs):
    log_record(PaymentStatus.CONFIRMED, *args, **kwargs)


def log_rejected(*args, **kwargs):
    log_record(PaymentStatus.REJECTED, *args, **kwargs)


def log_refunded(*args, **kwargs):
    log_record(PaymentStatus.REFUNDED, *args, **kwargs)


def log_error(*args, **kwargs):
    log_record(PaymentStatus.ERROR, *args, **kwargs)
