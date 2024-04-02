
import django_filters
from django.db.models import Q

from apps.bases.filters import BaseFilterOrderBy

from .models import (
    ClientDetails,
    Company,
    PromoCode,
    TrackUserLogin,
    UnitOfHistory,
    User,
    UserPromoCode,
)


class ClientDetailsFilters(BaseFilterOrderBy):
    """
        Client Filter will define here
    """

    class Meta:
        model = ClientDetails
        fields = [
            'id',
        ]


class UserFilters(BaseFilterOrderBy):
    """
        User Filter will define here
    """
    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains'
    )
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )
    created_on = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='exact'
    )
    updated_on = django_filters.CharFilter(
        field_name='updated_on__date', lookup_expr='exact'
    )
    start = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='gte'
    )
    end = django_filters.CharFilter(
        field_name='created_on__date', lookup_expr='lte'
    )
    is_blocked = django_filters.BooleanFilter(
        method='is_blocked_filter'
    )

    def is_blocked_filter(self, qs, name, value):
        if value:
            qs = qs.filter(
                is_active=False, deactivation_reason=''
            )
        else:
            qs = qs.exclude(
                is_active=False, deactivation_reason=''
            )
        return qs

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'gender',
            'term_and_condition_accepted',
            'privacy_policy_accepted',
            'is_email_verified',
            'is_phone_verified',
            'is_verified',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_deleted',
        ]


class LogsFilters(BaseFilterOrderBy):
    """
        User history Filter will define here
    """
    action = django_filters.CharFilter(
        field_name='action',
        lookup_expr='icontains'
    )
    user = django_filters.CharFilter(
        method='user_filter'
    )
    perform_for = django_filters.CharFilter(
        field_name='perform_for__email',
        lookup_expr='icontains'
    )
    reference_id = django_filters.CharFilter(
        field_name='object_id',
        lookup_expr='icontains'
    )
    content_type = django_filters.CharFilter(
        field_name='content_type__model',
        lookup_expr='icontains'
    )
    created_on = django_filters.CharFilter(
        field_name='created__date', lookup_expr='exact'
    )
    start = django_filters.CharFilter(
        field_name='created__date', lookup_expr='gte'
    )
    end = django_filters.CharFilter(
        field_name='created__date', lookup_expr='lte'
    )

    def user_filter(self, qs, name, value):
        if value:
            qs = qs.filter(
                Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value)
            )
        return qs

    class Meta:
        model = UnitOfHistory
        fields = [
            'id',
            'action',
            'user',
            'perform_for',
            'reference_id',
            'content_type'
        ]


class CompanyFilters(BaseFilterOrderBy):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )
    working_email = django_filters.CharFilter(
        field_name='working_email',
        lookup_expr='icontains'
    )

    class Meta:
        model = Company
        fields = [
            'id',
        ]


class TrackUserLoginFilters(BaseFilterOrderBy):
    id = django_filters.CharFilter(
        field_name='id',
        lookup_expr='exact'
    )
    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )

    class Meta:
        model = TrackUserLogin
        fields = [
            'id',
        ]


class PromoCodeFilters(BaseFilterOrderBy):
    id = django_filters.CharFilter(
        field_name='id',
        lookup_expr='exact'
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = PromoCode
        fields = [
            'id',
        ]


class UserPromoCodeFilters(BaseFilterOrderBy):
    id = django_filters.CharFilter(
        field_name='id',
        lookup_expr='exact'
    )
    promo_code = django_filters.CharFilter(
        field_name='promo_code__id',
        lookup_expr='icontains'
    )

    class Meta:
        model = UserPromoCode
        fields = [
            'id',
        ]
