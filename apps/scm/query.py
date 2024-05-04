# third party imports

import graphene
from django.contrib.auth import get_user_model
from graphene_django.filter.fields import DjangoFilterConnectionField

from backend.permissions import is_authenticated

from .models import Category, FoodMeeting, Product
from .object_types import (
    CategoryType,
    FoodMeetingType,
    Ingredient,
    IngredientType,
    ProductType,
)

# local imports

User = get_user_model()


class CategoryQuery(graphene.ObjectType):
    """
        query all category information
    """
    category = graphene.Field(CategoryType, id=graphene.ID())
    categories = DjangoFilterConnectionField(CategoryType, max_limit=None)

    def resolve_category(self, info, id, **kwargs):
        return Category.objects.filter(id=id, is_deleted=False).last()

    def resolve_categories(self, info, **kwargs):
        return Category.objects.filter(is_deleted=False)


class Query(CategoryQuery, graphene.ObjectType):
    """
        query all table information.
    """
    products = DjangoFilterConnectionField(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID())
    ingredients = DjangoFilterConnectionField(IngredientType)
    ingredient = graphene.Field(IngredientType, id=graphene.ID())
    food_meetings = DjangoFilterConnectionField(FoodMeetingType)
    food_meeting = graphene.Field(FoodMeetingType, id=graphene.ID())

    def resolve_products(self, info, **kwargs):
        user = info.context.user
        if user and user.is_admin:
            qs = Product.objects.all()
        elif user and user.is_vendor:
            qs = Product.objects.filter(vendor=user.vendor)
        else:
            qs = Product.queryset()
        return qs

    def resolve_product(self, info, id, **kwargs):
        user = info.context.user
        if user and user.is_admin:
            qs = Product.objects.filter(id=id)
        elif user and user.is_vendor:
            qs = Product.objects.filter(vendor=user.vendor, id=id)
        else:
            qs = Product.queryset().filter(id=id)
        return qs.last()

    def resolve_ingredients(self, info, **kwargs):
        user = info.context.user
        if user and user.is_admin:
            qs = Ingredient.objects.all()
        else:
            qs = Ingredient.queryset()
        return qs

    def resolve_ingredient(self, info, id, **kwargs):
        user = info.context.user
        if user and user.is_admin:
            qs = Ingredient.objects.filter(id=id)
        else:
            qs = Ingredient.queryset().filter(id=id)
        return qs.last()

    @is_authenticated
    def resolve_food_meetings(self, info, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = FoodMeeting.objects.all()
        else:
            qs = FoodMeeting.objects.filter(company=user.company)
        return qs

    @is_authenticated
    def resolve_food_meeting(self, info, id, **kwargs):
        user = info.context.user
        if user.is_admin:
            qs = FoodMeeting.objects.filter(id=id)
        else:
            qs = FoodMeeting.objects.filter(company=user.company, id=id)
        return qs.last()
