
import graphene
from django.contrib.auth import get_user_model
from graphene.types.generic import GenericScalar

from backend.permissions import is_admin_user, is_vendor_user

User = get_user_model()


class AdminDashboard:

    def __init__(self):
        pass

    def get_sold_products(self):
        pass

    def get_sales_history(self):
        pass


class VendorDashboard:

    def __init__(self):
        pass

    def get_sold_products(self):
        pass

    def get_sold_history(self):
        pass


class AnalyticsType(graphene.ObjectType):
    data = GenericScalar()


class Query(graphene.ObjectType):
    """
        define all queries together
    """
    admin_dashboard = graphene.Field(
        AnalyticsType
    )
    vendor_dashboard = graphene.Field(
        AnalyticsType
    )

    @is_admin_user
    def resolve_admin_dashboard(self, info, **kwargs):

        return None

    @is_vendor_user
    def resolve_vendor_dashboard(self, info, **kwargs):

        return None
