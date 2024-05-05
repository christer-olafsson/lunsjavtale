from django.db import models


class PaymentTypeChoices(models.TextChoices):
    ONLINE = 'online'
    PAY_BY_INVOICE = 'pay-by-invoice'
    CASH_ON_DELIVERY = 'cash-on-delivery'


class InvoiceStatusChoices(models.TextChoices):
    """
        define selection fields for status choice
    """
    PLACED = 'Placed'
    CONFIRMED = 'Confirmed'
    PARTIALLY_PAID = 'Partially-paid'
    PAYMENT_COMPLETED = 'Payment-completed'
    CANCELLED = 'Cancelled'


class DecisionChoices(models.TextChoices):
    """
        define selection fields for decision choice
    """
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'


STATUS_MAPPING = {
    '0': InvoiceStatusChoices.PLACED,
    '1': InvoiceStatusChoices.CONFIRMED,
    '2': InvoiceStatusChoices.PARTIALLY_PAID,
    '3': InvoiceStatusChoices.PAYMENT_COMPLETED,
    '4': InvoiceStatusChoices.CANCELLED,
}
