# third party imports

import graphene
from django.contrib.auth import get_user_model
from django.db.models import Q
from graphene_django.filter.fields import DjangoFilterConnectionField

from backend.permissions import is_authenticated

from ..users.choices import RoleTypeChoices
from .models import Order, OrderPayment, PaymentMethod, ProductRating, SellCart
from .object_types import (
    OrderPaymentType,
    OrderType,
    PaymentMethodType,
    ProductRatingType,
    SellCartType,
)

# local imports

User = get_user_model()


class Query(graphene.ObjectType):
    """
        query all table information.
    """
    payment_methods = DjangoFilterConnectionField(PaymentMethodType)
    payment_method = graphene.Field(PaymentMethodType, id=graphene.ID())
    added_carts = DjangoFilterConnectionField(SellCartType)
    cart = graphene.Field(SellCartType, id=graphene.ID())
    orders = DjangoFilterConnectionField(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID())
    order_payments = DjangoFilterConnectionField(OrderPaymentType)
    order_payment = graphene.Field(OrderPaymentType, id=graphene.ID())
    product_ratings = DjangoFilterConnectionField(ProductRatingType)
    product_rating = graphene.Field(ProductRatingType, id=graphene.ID())

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

    @is_authenticated
    def resolve_orders(self, info, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = Order.objects.all()
        else:
            qs = Order.objects.filter(company=user.company)
        return qs

    @is_authenticated
    def resolve_order(self, info, id, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = Order.objects.filter(id=id)
        else:
            qs = Order.objects.filter(company=user.company, id=id)
        return qs.last()

    @is_authenticated
    def resolve_order_payments(self, info, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = OrderPayment.objects.all()
        elif user.role in [RoleTypeChoices.OWNER, RoleTypeChoices.MANAGER]:
            qs = OrderPayment.objects.filter(Q(order__company=user.company) | Q(user_cart__added_for=user))
        else:
            qs = OrderPayment.objects.filter(user_cart__added_for=user)
        return qs

    @is_authenticated
    def resolve_order_payment(self, info, id, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = OrderPayment.objects.filter(id=id)
        elif user.role in [RoleTypeChoices.OWNER, RoleTypeChoices.MANAGER]:
            qs = OrderPayment.objects.filter(Q(order__company=user.company) | Q(user_cart__added_for=user), id=id)
        else:
            qs = OrderPayment.objects.filter(user_cart__added_for=user, id=id)
        return qs.last()

    @is_authenticated
    def resolve_product_ratings(self, info, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = ProductRating.objects.all()
        else:
            qs = ProductRating.objects.filter(added_by=user)
        return qs

    @is_authenticated
    def resolve_product_rating(self, info, id, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = ProductRating.objects.filter(id=id)
        else:
            qs = ProductRating.objects.filter(added_by=user, id=id)
        return qs.last()

    @is_authenticated
    def resolve_added_carts(self, info, **kwargs):
        user = info.context.user
        qs = SellCart.objects.filter(added_by=user)
        return qs

    @is_authenticated
    def resolve_cart(self, info, id, **kwargs):
        qs = SellCart.objects.filter(id=id)
        return qs.last()
