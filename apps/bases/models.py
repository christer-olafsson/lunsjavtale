
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class BaseModel(models.Model):
    """Define all common fields for all table with id field."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )  # generate unique id.
    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate
    updated_on = models.DateTimeField(
        auto_now=True
    )  # object update time. will automatically generate

    class Meta:
        abstract = True  # define this table/model is abstract


class BaseWithoutID(models.Model):
    """Define all common fields for all table."""

    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate
    updated_on = models.DateTimeField(
        auto_now=True
    )  # object update time. will automatically generate

    class Meta:
        abstract = True  # define this table/model is abstract


class BasePriceModel(models.Model):
    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        default=1
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="price after discount",
        default=1,
        blank=True
    )
    tax_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        default=50
    )
    price_with_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="price adding TAX & discount",
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.tax_percent = settings.TAX_PERCENTAGE if self.tax_percent is None else self.tax_percent
        # price_with_tax = self.actual_price + ((self.vat_percent * self.actual_price) / 100)
        self.discount_percent = self.discount_percent if self.discount_percent else 0
        price_after_discount = self.actual_price - ((self.discount_percent * self.actual_price) / 100)
        self.price = price_after_discount
        self.price_with_tax = price_after_discount + ((self.tax_percent * price_after_discount) / 100)
        super(BasePriceModel, self).save(*args, **kwargs)
