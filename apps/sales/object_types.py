
# third party imports
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

# local imports
from apps.sales.filters import (
    OrderFilters,
    OrderPaymentFilters,
    PaymentMethodFilters,
    ProductRatingFilters,
    SellCartFilters,
    UserCartFilters,
)
from backend.count_connection import CountConnection

from .models import (
    Order,
    OrderPayment,
    PaymentMethod,
    ProductRating,
    SellCart,
    UserCart,
)


class PaymentMethodType(DjangoObjectType):
    """
        define django object type for PaymentMethod model with PaymentMethod filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = PaymentMethod
        filterset_class = PaymentMethodFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class SellCartType(DjangoObjectType):
    """
        define django object type for SellCart model with SellCart filter-set
    """
    id = graphene.ID(required=True)
    ordered_quantity = graphene.Int()

    class Meta:
        model = SellCart
        filterset_class = SellCartFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection

    def resolve_ordered_quantity(self, info, **kwargs):
        return self.ordered_quantity


class UserCartType(DjangoObjectType):
    """
        define django object type for UserCart model with UserCart filter-set
    """
    id = graphene.ID(required=True)
    is_full_paid = graphene.Boolean()

    class Meta:
        model = UserCart
        filterset_class = UserCartFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection

    def resolve_is_full_paid(self, info, **kwargs):
        return self.is_full_paid


class OrderType(DjangoObjectType):
    """
        define django object type for Order model with Order filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = Order
        filterset_class = OrderFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class OrderSummaryType(graphene.ObjectType):
    """
    """
    added_carts = DjangoFilterConnectionField(SellCartType)
    actual_price = graphene.Decimal()
    shipping_charge = graphene.Decimal()
    final_price = graphene.Decimal()


class OrderPaymentType(DjangoObjectType):
    """
        define django object type for OrderPayment model with OrderPayment filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = OrderPayment
        filterset_class = OrderPaymentFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class ProductRatingType(DjangoObjectType):
    """
        define django object type for ProductRating model with ProductRating filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = ProductRating
        filterset_class = ProductRatingFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection
