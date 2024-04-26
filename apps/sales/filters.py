
import django_filters
from django.db.models import Q

from apps.bases.filters import BaseFilterOrderBy

from .models import Category, Ingredient, Product, ProductAttachment


class CategoryFilters(BaseFilterOrderBy):
    """
        Category Filters will define here
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    # parent = django_filters.CharFilter(
    #     field_name='parent__id',
    #     lookup_expr='exact'
    # )
    parent = django_filters.CharFilter(
        method='parent_filter'
    )

    def parent_filter(self, qs, name, value):
        if value == '0':
            qs = qs.filter(parent__isnull=True)
        elif value:
            try:
                qs = qs.filter(parent_id=value)
            except Exception:
                qs = qs.filter(id=None)
        return qs

    class Meta:
        model = Category
        fields = [
            'id',
            'is_active',
            'name',
        ]


class ProductFilters(BaseFilterOrderBy):
    """
        Product filters will be defined here
    """
    title = django_filters.CharFilter(
        method="title_filter",
    )
    category = django_filters.CharFilter(
        field_name='category__id', lookup_expr='exact'
    )
    created_on = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='exact'
    )
    updated_on = django_filters.CharFilter(
        field_name='updated_on__date', lookup_expr='exact'
    )
    start = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='gte'
    )
    end = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='lte'
    )
    min_price = django_filters.CharFilter(
        field_name='price', lookup_expr='gte'
    )
    max_price = django_filters.CharFilter(
        field_name='price', lookup_expr='lte'
    )

    def title_filter(self, qs, name, value):
        if value:
            qs = qs.filter(Q(title__icontains=value) | Q(description__icontains=value) | Q(SKU__icontains=value))
        return qs

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'availability',
            'is_deleted',
        ]


class IngredientFilters(BaseFilterOrderBy):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'is_active',
            'is_deleted',
        ]


class ProductAttachmentFilters(BaseFilterOrderBy):

    class Meta:
        model = ProductAttachment
        fields = [
            'id',
            'is_cover',
        ]
