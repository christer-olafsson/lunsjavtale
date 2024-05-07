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
    UPDATED = 'updated'
    CANCELLED = 'Cancelled'
    CONFIRMED = 'Confirmed'
    PARTIALLY_PAID = 'Partially-paid'
    PAYMENT_PENDING = 'Payment-pending'
    PAYMENT_COMPLETED = 'Payment-completed'


class DecisionChoices(models.TextChoices):
    """
        define selection fields for decision choice
    """
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'


STATUS_MAPPING = {
    '0': InvoiceStatusChoices.PLACED,
    '1': InvoiceStatusChoices.UPDATED,
    '2': InvoiceStatusChoices.CONFIRMED,
    '3': InvoiceStatusChoices.PARTIALLY_PAID,
    '4': InvoiceStatusChoices.PAYMENT_COMPLETED,
    '5': InvoiceStatusChoices.CANCELLED,
}
