
import django_filters

from apps.bases.filters import BaseFilterOrderBy

from .models import (
    BillingAddress,
    Order,
    OrderPayment,
    OrderStatus,
    PaymentMethod,
    ProductRating,
    SellCart,
    UserCart,
)


class PaymentMethodFilters(BaseFilterOrderBy):
    """
        PaymentMethod Filters will define here
    """
    card_number = django_filters.CharFilter(
        field_name='card_number',
        lookup_expr='icontains'
    )

    class Meta:
        model = PaymentMethod
        fields = [
            'id',
        ]


class SellCartFilters(BaseFilterOrderBy):
    """
        SellCart Filters will define here
    """
    item = django_filters.CharFilter(
        field_name='item__id', lookup_expr='exact'
    )

    class Meta:
        model = SellCart
        fields = [
            'id',
            'date',
        ]


class UserCartFilters(BaseFilterOrderBy):
    """
        UserCart Filters will define here
    """

    class Meta:
        model = UserCart
        fields = [
            'id',
        ]


class OrderFilters(BaseFilterOrderBy):
    """
        Order Filters will define here
    """
    company = django_filters.CharFilter(
        field_name="company__id", lookup_expr="exact"
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
        ]


class BillingAddressFilters(BaseFilterOrderBy):
    """
        BillingAddress Filters will define here
    """

    class Meta:
        model = BillingAddress
        fields = [
            'id',
        ]


class OrderStatusFilters(BaseFilterOrderBy):
    """
        Order status Filters will define here
    """
    order = django_filters.CharFilter(
        field_name="order__id", lookup_expr="exact"
    )

    class Meta:
        model = OrderStatus
        fields = [
            'id',
        ]


class OrderPaymentFilters(BaseFilterOrderBy):
    """
        OrderPayment Filters will define here
    """
    company = django_filters.CharFilter(
        field_name="order__company__id", lookup_expr="exact"
    )
    user = django_filters.CharFilter(
        field_name="user_cart__added_for__id", lookup_expr="exact"
    )

    class Meta:
        model = OrderPayment
        fields = [
            'id',
        ]


class ProductRatingFilters(BaseFilterOrderBy):
    """
        ProductRating Filters will define here
    """
    product = django_filters.CharFilter(
        field_name="product__id", lookup_expr="exact"
    )
    added_by = django_filters.CharFilter(
        field_name="added_by__id", lookup_expr="exact"
    )

    class Meta:
        model = ProductRating
        fields = [
            'id',
        ]
