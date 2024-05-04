from django import forms
from django.contrib.auth import get_user_model

from .models import PaymentMethod, ProductRating

User = get_user_model()


class PaymentMethodForm(forms.ModelForm):
    """
        PaymentMethod model form will define here
    """

    class Meta:
        model = PaymentMethod
        exclude = ['user']


class ProductRatingForm(forms.ModelForm):
    """
        ProductRating model form will define here
    """

    class Meta:
        model = ProductRating
        exclude = ['added_by']
