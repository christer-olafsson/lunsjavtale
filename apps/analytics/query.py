
import graphene
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from graphene.types.generic import GenericScalar

from apps.bases.utils import get_serialized_data
from apps.sales.models import Order, ProductRating
from apps.users.choices import RoleTypeChoices
from apps.users.models import Company
from backend.permissions import is_admin_user, is_vendor_user

User = get_user_model()


class AdminDashboard:

    def __init__(self):
        pass

    def get_data(self):
        context = {
            'totalCustomers': Company.objects.count(),
            'totalOrders': Order.objects.count(),
            'totalSales': str(Order.objects.aggregate(tot=Sum('final_price'))['tot'] or '0.00'),
            'salesToday': str(Order.objects.filter(
                created_on__date=timezone.now().date()
            ).aggregate(tot=Sum('final_price'))['tot'] or '0.00'),
            'recentCustomers': self.get_recent_customers(),
            'recentOrders': self.get_recent_orders(),
            'users': self.get_users(),
            'recentReviews': self.get_recent_ratings(),
        }
        return context

    def get_recent_customers(self):
        return get_serialized_data(
            Company.objects.order_by('-created_on')[:4], fields=['name', 'email', 'contact']
        )

    def get_recent_orders(self):
        return get_serialized_data(
            Order.objects.order_by('-created_on')[:4], fields=['company__name', 'final_price', 'delivery_date']
        )

    def get_users(self):
        return get_serialized_data(
            User.objects.filter(
                role__in=[RoleTypeChoices.ADMIN, RoleTypeChoices.DEVELOPER]
            )[:4], fields=['first_name', 'last_name', 'email', 'photo_url', 'role']
        )

    def get_recent_ratings(self):
        return get_serialized_data(
            ProductRating.objects.order_by('-created_on')[:4],
            fields=['added_by__first_name', 'added_by__last_name', 'product__name', 'rating', 'description']
        )

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
        data = AdminDashboard().get_data()
        return AnalyticsType(
            data=data
        )

    @is_vendor_user
    def resolve_vendor_dashboard(self, info, **kwargs):

        return None
