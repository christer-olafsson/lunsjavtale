from django import forms
from django.contrib.auth import get_user_model

from .models import Category, FoodMeeting, Ingredient, Product

User = get_user_model()


class ProductForm(forms.ModelForm):
    """
        Product model form will define here
    """

    class Meta:
        model = Product
        fields = "__all__"


class CategoryForm(forms.ModelForm):
    """
        category model form will define here
    """

    class Meta:
        model = Category
        exclude = ['is_deleted', 'deleted_on']


class FoodMeetingForm(forms.ModelForm):
    """
        Food Meeting model form will define here
    """

    class Meta:
        model = FoodMeeting
        exclude = ['is_contacted', 'note']


class IngredientForm(forms.ModelForm):
    """
        Ingredient model form will define here
    """

    class Meta:
        model = Ingredient
        fields = '__all__'
