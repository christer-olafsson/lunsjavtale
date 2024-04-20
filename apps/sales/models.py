from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.bases.models import BaseWithoutID, SoftDeletion
from apps.sales.choices import InvoiceStatusChoices, PaymentTypeChoices


class PaymentMethod(BaseWithoutID, SoftDeletion):
    user = models.ForeignKey(
        to='users.User', on_delete=models.DO_NOTHING, related_name='payment_methods'
    )
    card_holder_name = models.CharField(max_length=128)
    card_number = models.CharField(max_length=128)
    CVV = models.CharField(max_length=6)
    expiry = models.DateField()
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_payment_methods"  # define table name for database
        ordering = ['-id']  # define default order as id in descending

    def save(self, *args, **kwargs):
        if self.is_default:
            self.user.payment_methods.exclude(id=self.pk).update(is_default=False)
        super(PaymentMethod, self).save(*args, **kwargs)


class SellCart(BaseWithoutID):
    added_by = models.ForeignKey(
        to='users.User', on_delete=models.SET_NULL, related_name='user_carts', blank=True, null=True
    )
    added_for = models.ManyToManyField(
        to='users.User', blank=True
    )
    date = models.DateField()
    invoice = models.ForeignKey(
        'Order', on_delete=models.DO_NOTHING, related_name='invoice_carts', blank=True, null=True)
    item = models.ForeignKey(to='scm.Product', on_delete=models.DO_NOTHING, related_name='product_carts')
    quantity = models.PositiveIntegerField(db_index=True, default=1, validators=[MinValueValidator(1)])
    cancelled = models.PositiveIntegerField(default=0)
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
        db_table = f"{settings.DB_PREFIX}_sell_carts"  # define table name for database


class UserCart(BaseWithoutID):
    cart = models.ForeignKey(
        to=SellCart, on_delete=models.DO_NOTHING, related_name='users'
    )
    added_for = models.ForeignKey(
        to='users.User', on_delete=models.DO_NOTHING, related_name='items'
    )
    payment_type = models.CharField(
        max_length=16, choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.PAY_BY_INVOICE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    ingredients = models.ManyToManyField(to='scm.Ingredient', blank=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_carts"  # define table name for database


class AlterCart(BaseWithoutID):
    base = models.ForeignKey(
        to=UserCart, on_delete=models.CASCADE, related_name='alter_histories'
    )
    previous_cart = models.ForeignKey(
        to=SellCart, on_delete=models.DO_NOTHING, related_name='users'
    )
    cart = models.ForeignKey(
        to=SellCart, on_delete=models.DO_NOTHING, related_name='users'
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_alter_carts"  # define table name for database


class Order(BaseWithoutID, SoftDeletion):
    company = models.ForeignKey(
        to='users.Company', on_delete=models.DO_NOTHING, related_name='orders'
    )
    shipping_address = models.ForeignKey(
        to='users.Address', on_delete=models.SET_NULL, related_name='orders', blank=True, null=True
    )
    created_by = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, related_name='created_orders')
    note = models.TextField(blank=True, null=True)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey('users.UserCoupon', on_delete=models.DO_NOTHING, blank=True, null=True)
    payment_type = models.CharField(
        max_length=16, choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.PAY_BY_INVOICE
    )
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


class OrderStatus(BaseWithoutID):
    order = models.ForeignKey(
        to=Order, on_delete=models.SET_NULL, related_name='statuses', blank=True, null=True
    )
    status = models.CharField(
        max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PLACED
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_order_statuses"  # define table name for database


class UserCartStatus(BaseWithoutID):
    user_cart = models.ForeignKey(
        to=UserCart, on_delete=models.SET_NULL, related_name='statuses'
    )
    status = models.CharField(
        max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PLACED
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_cart_statuses"  # define table name for database


class OrderPayment(BaseWithoutID):
    order = models.ForeignKey(
        to=Order, on_delete=models.SET_NULL, related_name='payments', blank=True, null=True
    )
    user_cart = models.ForeignKey(
        to=UserCart, on_delete=models.SET_NULL, related_name='payments', blank=True, null=True
    )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    note = models.TextField(blank=True, null=True)
    payment_info = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, related_name='created_orders')

    class Meta:
        db_table = f"{settings.DB_PREFIX}_order_payments"  # define table name for database


class ProductRating(models.Model):
    added_by = models.ForeignKey(
        to='users.User', on_delete=models.DO_NOTHING, related_name='user_ratings'
    )
    product = models.ForeignKey(to='scm.Product', on_delete=models.DO_NOTHING, related_name='product_ratings')
    rating = models.PositiveIntegerField(
        db_index=True, default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate

    class Meta:
        db_table = f"{settings.DB_PREFIX}_product_ratings"  # define table name for database
        ordering = ['-id']  # define default order as id in descending
