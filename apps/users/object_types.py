# at backend/users/schema.py

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

# local imports
from backend.count_connection import CountConnection

from .filters import (
    ClientDetailsFilters,
    CompanyFilters,
    LogsFilters,
    PromoCodeFilters,
    TrackUserLoginFilters,
    UserFilters,
    UserPromoCodeFilters,
)
from .models import (
    Agreement,
    ClientDetails,
    Company,
    PromoCode,
    TrackUserLogin,
    UnitOfHistory,
    UserDeviceToken,
    UserPromoCode,
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
            'notification_set', 'user_notifications_viewed', 'performer', 'perform_for'
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


class PromoCodeType(DjangoObjectType):
    id = graphene.ID(required=True)

    class Meta:
        model = PromoCode
        filterset_class = PromoCodeFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection


class UserPromoCodeType(DjangoObjectType):
    id = graphene.ID(required=True)

    class Meta:
        model = UserPromoCode
        filterset_class = UserPromoCodeFilters
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
