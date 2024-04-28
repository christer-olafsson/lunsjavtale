from django import forms
from django.contrib.auth import get_user_model

from .models import PaymentMethod

User = get_user_model()


class PaymentMethodForm(forms.ModelForm):
    """
        PaymentMethod model form will define here
    """

    class Meta:
        model = PaymentMethod
        exclude = ['user']
