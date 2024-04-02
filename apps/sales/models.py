from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.bases.models import BaseWithoutID
from apps.sales.choices import InvoiceStatusChoices, PaymentTypeChoices


class SellCart(BaseWithoutID):
    added_by = models.ForeignKey(
        to='users.User', on_delete=models.SET_NULL, related_name='user_carts', blank=True, null=True
    )
    added_for = models.ManyToManyField(
        to='users.User', blank=True
    )
    invoice = models.ForeignKey(
        'Invoice', on_delete=models.DO_NOTHING, related_name='invoice_carts', blank=True, null=True)
    item = models.ForeignKey(to='scm.Product', on_delete=models.DO_NOTHING, related_name='invoice_products')
    quantity = models.PositiveIntegerField(db_index=True, default=1, validators=[MinValueValidator(1)])
    returned = models.PositiveIntegerField(default=0)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_with_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_sell-carts"  # define table name for database


class Order(BaseWithoutID):
    company = models.ForeignKey(
        to='users.Company', on_delete=models.DO_NOTHING, related_name='b2b_invoices', blank=True, null=True
    )
    shipping_address = models.ForeignKey(
        to='users.Address', on_delete=models.DO_NOTHING, related_name='orders'
    )
    created_by = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, related_name='created_orders')
    note = models.TextField(blank=True, null=True)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PROCESSING)
    promo_code = models.ForeignKey('users.UserPromoCode', on_delete=models.DO_NOTHING, blank=True, null=True)
    payment_type = models.CharField(max_length=16, choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.CASH)
    requested_delivery_date = models.DateField(blank=True, null=True)
    vat_percent = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=5
    )
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="price adding vat & discount",
        default=1
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_orders"  # define table name for database
        ordering = ['-id']  # define default order as id in descending


class InvoiceReceipt(BaseWithoutID):
    company = models.ForeignKey(
        to='users.Company', on_delete=models.DO_NOTHING, related_name='b2b_invoices', blank=True, null=True
    )
    invoice = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='receipts')
    note = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, related_name='created_orders')

    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_invoice_receipts"  # define table name for database
        ordering = ['-id']  # define default order as id in descending
