
# third party imports
import graphene
from graphene_django import DjangoObjectType

# local imports
from apps.scm.filters import (
    CategoryFilters,
    IngredientFilters,
    ProductAttachmentFilters,
    ProductFilters,
)
from backend.count_connection import CountConnection

from .models import Category, Ingredient, Product, ProductAttachment


class CategoryType(DjangoObjectType):
    """
        define django object type for category model with category filter-set
    """
    id = graphene.ID(required=True)
    products_added = graphene.Int()

    class Meta:
        model = Category
        filterset_class = CategoryFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_products_added(self, info):
        return self.products.count()


class ProductType(DjangoObjectType):
    """
        define django object type for product model with product filter-set
    """
    id = graphene.ID(required=True)
    final_price = graphene.Decimal()
    discount_percent = graphene.Decimal()

    class Meta:
        model = Product
        filterset_class = ProductFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_final_price(self, info, **kwargs):
        return self.price_with_tax

    @staticmethod
    def resolve_discount_percent(self, info, **kwargs):
        return self.discount_percent or "0.00"


class IngredientType(DjangoObjectType):
    """
        define django object type for Ingredient model with filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = Ingredient
        filterset_class = IngredientFilters
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection


class ProductAttachmentType(DjangoObjectType):
    """
        define django object type for ProductAttachment model with filter-set
    """
    id = graphene.ID(required=True)

    class Meta:
        model = ProductAttachment
        filterset_class = ProductAttachmentFilters
        exclude = ['product']
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        connection_class = CountConnection
