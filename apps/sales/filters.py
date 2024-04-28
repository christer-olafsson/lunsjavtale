
import django_filters

from apps.bases.filters import BaseFilterOrderBy

from .models import PaymentMethod


class PaymentMethodFilters(BaseFilterOrderBy):
    """
        PaymentMethod Filters will define here
    """
    card_number = django_filters.CharFilter(
        field_name='card_number',
        lookup_expr='icontains'
    )

    class Meta:
        model = PaymentMethod
        fields = [
            'id',
        ]
