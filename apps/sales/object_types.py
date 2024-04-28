
# third party imports
import graphene
from graphene_django import DjangoObjectType

# local imports
from apps.sales.filters import PaymentMethodFilters
from backend.count_connection import CountConnection

from .models import PaymentMethod


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
