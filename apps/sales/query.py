# third party imports

import graphene
from django.contrib.auth import get_user_model
from graphene_django.filter.fields import DjangoFilterConnectionField

from backend.permissions import is_authenticated

from .models import PaymentMethod
from .object_types import PaymentMethodType

# local imports

User = get_user_model()


class Query(graphene.ObjectType):
    """
        query all advertise information.
        pass category name for category parameter
        and city id for city parameter
    """
    payment_methods = DjangoFilterConnectionField(PaymentMethodType)
    payment_method = graphene.Field(PaymentMethodType, id=graphene.ID())

    @is_authenticated
    def resolve_payment_methods(self, info, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = PaymentMethod.objects.all()
        else:
            qs = PaymentMethod.objects.filter(user=user)
        return qs

    @is_authenticated
    def resolve_payment_method(self, info, id, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = PaymentMethod.objects.filter(id=id)
        else:
            qs = PaymentMethod.objects.filter(user=user, id=id)
        return qs.last()
