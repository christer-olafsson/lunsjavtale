from django.db import models


class PaymentTypeChoices(models.TextChoices):
    CASH_ON_DELIVERY = 'cash-on-delivery'
    ONLINE = 'online'
    PAY_BY_INVOICE = 'pay-by-invoice'


class InvoiceStatusChoices(models.TextChoices):
    """
        define selection fields for status choice
    """
    PROCESSING = 'Processing'
    PLACED = 'Placed'
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    COMPLETE = 'Complete'
    CANCELLED = 'Cancelled'
    ERRORED = 'Errored'


STATUS_MAPPING = {
    '0': InvoiceStatusChoices.PROCESSING,
    '1': InvoiceStatusChoices.PLACED,
    '2': InvoiceStatusChoices.PENDING,
    '3': InvoiceStatusChoices.SHIPPED,
    '4': InvoiceStatusChoices.COMPLETE,
    '5': InvoiceStatusChoices.CANCELLED,
    '6': InvoiceStatusChoices.ERRORED,
}
