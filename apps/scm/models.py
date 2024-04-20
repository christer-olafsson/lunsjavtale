from django.conf import settings
from django.db import models

from apps.bases.models import BasePriceModel, BaseWithoutID


class Ingredient(BaseWithoutID):
    """
    """
    name = models.CharField(max_length=64)  # define ingredient name
    description = models.TextField(
        blank=True, null=True,
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_ingredients"  # define table name for database
        ordering = ['-id']  # define default order as id in descending

    @classmethod
    def queryset(cls):
        return cls.objects.filter(is_deleted=False)


class Category(BaseWithoutID):
    """
        Store category information by making a hierarchy of category and sub-category
    """
    name = models.CharField(max_length=64)  # define category name
    description = models.TextField(
        blank=True, null=True,
        help_text="Category description for showing over page."
    )
    parent = models.ForeignKey(
        to='self', on_delete=models.SET_NULL, related_name='children', blank=True, null=True
    )  # define the category for any sub-category
    # slug = models.SlugField(blank=True, null=True, unique=True, max_length=96)
    logo_url = models.TextField(
        blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_categories"  # define table name for database
        verbose_name_plural = 'Categories'
        ordering = ['-id']  # define default order as id in descending
        unique_together = ('name', 'parent')

    @classmethod
    def queryset(cls):
        return cls.objects.filter(is_deleted=False)


class Product(BaseWithoutID, BasePriceModel):
    """
        product posting minimum required fields will define here
    """
    name = models.CharField(max_length=128)  # name of the product
    title = models.CharField(max_length=128, blank=True, null=True)  # name of the product
    description = models.TextField()  # some details about the product
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='products', null=True
    )  # define the category of the product
    contains = models.JSONField(blank=True, null=True)
    ingredients = models.ManyToManyField(to=Ingredient, blank=True)
    availability = models.BooleanField(default=True)  # if it is available or not
    # slug = models.SlugField(blank=True, null=True, unique=True, max_length=128)
    stock = models.PositiveIntegerField(default=0)  # store product stock
    visitor_count = models.PositiveIntegerField(default=0, null=True)  # store product visits
    is_adjustable_for_single_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_products"  # define table name for database
        ordering = ['-id']  # define default order as created in descending
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        # unique_together = ('title', 'category')

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def queryset(cls):
        return cls.objects.filter(is_deleted=False)


class ProductAttachment(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='attachments')
    file_url = models.TextField()
    is_cover = models.BooleanField(default=False)
    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate

    class Meta:
        db_table = f"{settings.DB_PREFIX}_product_attachments"  # define table name for database
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.is_cover:
            self.product.attachments.exclude(id=self.pk).update(is_cover=False)
        super(ProductAttachment, self).save(*args, **kwargs)
