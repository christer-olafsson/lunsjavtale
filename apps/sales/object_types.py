
# third party imports
import graphene
from graphene_django import DjangoObjectType

# local imports
from apps.sales.filters import PaymentMethodFilters, SellCartFilters
from backend.count_connection import CountConnection

from .models import PaymentMethod, SellCart


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
    total_price = graphene.Decimal()
    total_price_with_tax = graphene.Decimal()

    class Meta:
        model = SellCart
        filterset_class = SellCartFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection

    def resolve_ordered_quantity(self, info, **kwargs):
        return self.ordered_quantity

    def resolve_total_price(self, info, **kwargs):
        return self.ordered_quantity * self.price

    def resolve_total_price_with_tax(self, info, **kwargs):
        return self.ordered_quantity * self.price_with_tax
