# at backend/users/schema.py

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

# local imports
from backend.count_connection import CountConnection

from .filters import (
    AddressFilters,
    ClientDetailsFilters,
    CompanyFilters,
    CouponFilters,
    LogsFilters,
    TrackUserLoginFilters,
    UserCouponFilters,
    UserFilters,
)
from .models import (
    Address,
    Agreement,
    ClientDetails,
    Company,
    Coupon,
    TrackUserLogin,
    UnitOfHistory,
    UserCoupon,
    UserDeviceToken,
)

User = get_user_model()  # variable taken for User model


class ClientDetailsType(DjangoObjectType):
    """
        Define django object type for Client-details model with filter-set and relay node information
    """
    id = graphene.ID(required=True)

    class Meta:
        model = ClientDetails
        filterset_class = ClientDetailsFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class UserType(DjangoObjectType):
    """
        Define django object type for user model with filter-set and relay node information
    """
    id = graphene.ID(required=True)
    is_admin = graphene.Boolean()

    class Meta:
        model = User
        exclude = (
            'performer', 'perform_for'
        )
        filterset_class = UserFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class LogType(DjangoObjectType):
    """
        Define django object type for user history model with filter-set and relay node information
    """
    id = graphene.ID(required=True)

    class Meta:
        model = UnitOfHistory
        filterset_class = LogsFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class CompanyType(DjangoObjectType):
    """
        Define django object type for user Company model with filter-set and relay node information
    """
    id = graphene.ID(required=True)

    class Meta:
        model = Company
        filterset_class = CompanyFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class UserDeviceTokenType(DjangoObjectType):
    """
        Define django object type for User Device Token model
    """
    id = graphene.ID(required=True)

    class Meta:
        model = UserDeviceToken


class TrackUserLoginType(DjangoObjectType):
    id = graphene.ID(required=True)

    class Meta:
        model = TrackUserLogin
        filterset_class = TrackUserLoginFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection


class CouponType(DjangoObjectType):
    id = graphene.ID(required=True)

    class Meta:
        model = Coupon
        filterset_class = CouponFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection


class UserCouponType(DjangoObjectType):
    id = graphene.ID(required=True)

    class Meta:
        model = UserCoupon
        filterset_class = UserCouponFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection


class AgreementType(DjangoObjectType):
    """
        Define django object type for user skill model with filter-set and relay node information.
        typeOf choices::
        1. terms-and-conditions
        2. privacy-policy
    """
    id = graphene.ID(required=True)

    class Meta:
        model = Agreement
        filter_fields = {
            'type_of': ['exact', ]
        }
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class AddressType(DjangoObjectType):
    """
    """
    id = graphene.ID(required=True)

    class Meta:
        model = Address
        filterset_class = AddressFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class AppliedCouponType(graphene.ObjectType):
    actual_price = graphene.Float()
    amount_discounted = graphene.Float()
    discounted_price = graphene.Float()
    discounted_value = graphene.String()
