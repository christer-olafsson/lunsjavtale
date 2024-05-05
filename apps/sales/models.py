from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.bases.models import BaseWithoutID, SoftDeletion
from apps.sales.choices import DecisionChoices, InvoiceStatusChoices, PaymentTypeChoices


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
    order = models.ForeignKey(
        to='Order', on_delete=models.DO_NOTHING, related_name='order_carts', blank=True, null=True
    )

    added_by = models.ForeignKey(
        to='users.User', on_delete=models.SET_NULL, related_name='added_carts', blank=True, null=True
    )

    item = models.ForeignKey(
        to='scm.Product', on_delete=models.DO_NOTHING, related_name='product_carts'
    )
    date = models.DateField()
    added_for = models.ManyToManyField(
        to='users.User', blank=True
    )
    cancelled_by = models.ManyToManyField(
        to='users.User', blank=True, related_name="cancelled_carts"
    )
    quantity = models.PositiveIntegerField(
        db_index=True, default=1, validators=[MinValueValidator(1)]
    )
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
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_price_with_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    ingredients = models.ManyToManyField(to='scm.Ingredient', blank=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_sell_carts"  # define table name for database

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.ordered_quantity
        self.total_price_with_tax = self.price_with_tax * self.ordered_quantity
        super(SellCart, self).save(*args, **kwargs)

    @property
    def ordered_quantity(self):
        return self.quantity - self.cancelled


class UserCart(BaseWithoutID):
    cart = models.ForeignKey(
        to=SellCart, on_delete=models.DO_NOTHING, related_name='users'
    )
    added_for = models.ForeignKey(
        to='users.User', on_delete=models.DO_NOTHING, related_name='cart_items'
    )
    payment_type = models.CharField(
        max_length=16, choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.PAY_BY_INVOICE
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    ingredients = models.ManyToManyField(to='scm.Ingredient', blank=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_carts"  # define table name for database

    @property
    def is_full_paid(self):
        return self.cart.price_with_tax <= self.paid_amount


class AlterCart(BaseWithoutID):
    base = models.ForeignKey(
        to=UserCart, on_delete=models.CASCADE, related_name='alter_histories'
    )
    previous_cart = models.ForeignKey(
        to=SellCart, on_delete=models.DO_NOTHING, related_name='previous_used_carts'
    )
    item = models.ForeignKey(
        to='scm.Product', on_delete=models.DO_NOTHING, related_name='alter_carts'
    )
    status = models.CharField(max_length=32, choices=DecisionChoices.choices, default=DecisionChoices.PENDING)

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
    coupon = models.ForeignKey('users.UserCoupon', on_delete=models.DO_NOTHING, blank=True, null=True)
    payment_type = models.CharField(
        max_length=16, choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.PAY_BY_INVOICE
    )
    delivery_date = models.DateField()
    company_allowance = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    shipping_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="price adding vat & discount",
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    vat_percent = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="price adding vat & discount",
        default=0
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PLACED
    )

    class Meta:
        db_table = f"{settings.DB_PREFIX}_orders"  # define table name for database
        ordering = ['-id']  # define default order as id in descending

    def save(self, *args, **kwargs):
        price_after_discount = self.actual_price - self.discount_amount
        self.final_price = price_after_discount + ((self.vat_percent * price_after_discount) / 100)
        super(Order, self).save(*args, **kwargs)


class OrderStatus(models.Model):
    order = models.ForeignKey(
        to=Order, on_delete=models.SET_NULL, related_name='statuses', blank=True, null=True
    )
    status = models.CharField(
        max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PLACED
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate

    class Meta:
        db_table = f"{settings.DB_PREFIX}_order_statuses"  # define table name for database

    def save(self, *args, **kwargs):
        super(OrderStatus, self).save(*args, **kwargs)
        self.order.status = self.order.statuses.latest('created_on').status
        self.order.save()


# class UserCartStatus(models.Model):
#     user_cart = models.ForeignKey(
#         to=UserCart, on_delete=models.SET_NULL, related_name='statuses'
#     )
#     status = models.CharField(
#         max_length=32, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.PLACED
#     )
#     created_on = models.DateTimeField(
#         auto_now_add=True
#     )  # object creation time. will automatically generate
#
#     class Meta:
#         db_table = f"{settings.DB_PREFIX}_user_cart_statuses"  # define table name for database


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
    created_by = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, related_name='created_payments')

    class Meta:
        db_table = f"{settings.DB_PREFIX}_order_payments"  # define table name for database


class ProductRating(BaseWithoutID):
    added_by = models.ForeignKey(
        to='users.User', on_delete=models.DO_NOTHING, related_name='user_ratings'
    )
    product = models.ForeignKey(to='scm.Product', on_delete=models.DO_NOTHING, related_name='product_ratings')
    rating = models.PositiveIntegerField(
        db_index=True, default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(null=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_product_ratings"  # define table name for database
        ordering = ['-id']  # define default order as id in descending
