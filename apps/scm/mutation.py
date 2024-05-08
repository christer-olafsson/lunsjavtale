import graphene
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphene_django.forms.types import DjangoFormInputObjectType
from graphql import GraphQLError

# local imports
from apps.bases.utils import camel_case_format, get_object_by_id
from backend.permissions import is_admin_user, is_authenticated, is_vendor_user

from .forms import (
    CategoryForm,
    FoodMeetingForm,
    IngredientForm,
    ProductForm,
    VendorProductForm,
)
from .models import Category, FoodMeeting, Ingredient, Product, ProductAttachment
from .object_types import CategoryType, FoodMeetingType, IngredientType, ProductType


class CategoryMutation(DjangoModelFormMutation):
    """
        update and create new Category information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(CategoryType)

    class Meta:
        form_class = CategoryForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = CategoryForm(data=input)
        object_id = None
        if form.data.get('id'):
            object_id = form.data['id']
            old_obj = get_object_by_id(Category, object_id)
            form = CategoryForm(data=input, instance=old_obj)
        form_data = form.data
        if form.is_valid():
            obj, created = Category.objects.update_or_create(id=object_id, defaults=form_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return CategoryMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class CategoryDeleteMutation(graphene.Mutation):
    """
    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_admin_user
    def mutate(self, info, id, **kwargs):
        obj = Category.objects.get(id=id, is_deleted=False)
        obj.is_deleted = True
        obj.deleted_on = timezone.now()
        obj.save()
        return CategoryDeleteMutation(
            success=True, message="Successfully deleted"
        )


class IngredientMutation(DjangoModelFormMutation):
    """
        update and create new Ingredient information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(IngredientType)

    class Meta:
        form_class = IngredientForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = IngredientForm(data=input)
        object_id = None
        if form.data.get('id'):
            object_id = form.data['id']
            old_obj = get_object_by_id(Ingredient, object_id)
            form = IngredientForm(data=input, instance=old_obj)
        form_data = form.data
        if form.is_valid():
            obj, created = Ingredient.objects.update_or_create(id=object_id, defaults=form_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return IngredientMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class FoodMeetingMutation(DjangoFormMutation):
    """
        update and create new FoodMeeting information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(FoodMeetingType)

    class Meta:
        form_class = FoodMeetingForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        form = FoodMeetingForm(data=input)
        if form.is_valid():
            obj = form.save()
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return FoodMeetingMutation(
            success=True, message="Successfully added", instance=obj
        )


class FoodMeetingResolve(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()
        note = graphene.String()

    @is_admin_user
    def mutate(self, info, id, note, **kwargs):
        obj = FoodMeeting.objects.get(id=id)
        obj.note = note
        obj.is_contacted = True
        obj.save()
        return FoodMeetingResolve(
            success=True, message="Succesfully resolved"
        )


class MeetingDeleteMutation(graphene.Mutation):
    """
    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_admin_user
    def mutate(self, info, id, **kwargs):
        obj = FoodMeeting.objects.get(id=id)
        obj.delete()
        return MeetingDeleteMutation(
            success=True, message="Successfully deleted"
        )


class ProductInput(DjangoFormInputObjectType):

    class Meta:
        form_class = ProductForm


class ProductAttachmentInput(graphene.InputObjectType):
    file_url = graphene.String()
    is_cover = graphene.Boolean()


class ProductMutation(graphene.Mutation):
    """
        update and create new Product information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(ProductType)

    class Arguments:
        input = ProductInput()
        ingredients = graphene.List(graphene.String)
        attachments = graphene.List(ProductAttachmentInput)

    @is_admin_user
    def mutate(self, info, input, ingredients, attachments=[], **kwargs):
        form = ProductForm(data=input)
        if form.data.get('id'):
            object_id = form.data['id']
            old_obj = get_object_by_id(Product, object_id)
            form = ProductForm(data=input, instance=old_obj)
        if form.is_valid():
            obj = form.save()
            obj.ingredients.clear()
            for ing in ingredients:
                obj.ingredients.add(Ingredient.objects.get_or_create(name=ing)[0])
            if attachments:
                obj.attachments.all().delete()
                for attach in attachments:
                    ProductAttachment.objects.create(
                        product=obj, file_url=attach.get('file_url'),
                        is_cover=attach.get('is_cover')
                    )
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return ProductMutation(
            success=True, message=f"Successfully {'added' if input.get('id') else 'updated'}", instance=obj
        )


class VendorProductInput(DjangoFormInputObjectType):

    class Meta:
        form_class = VendorProductForm


class VendorProductMutation(graphene.Mutation):
    """
        update and create new Product information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(ProductType)

    class Arguments:
        input = VendorProductInput()
        ingredients = graphene.List(graphene.String)
        attachments = graphene.List(ProductAttachmentInput)

    @is_vendor_user
    def mutate(self, info, input, ingredients, attachments=[], **kwargs):
        user = info.context.user
        form = ProductForm(data=input)
        if form.data.get('id'):
            object_id = form.data['id']
            old_obj = get_object_by_id(Product, object_id)
            form = ProductForm(data=input, instance=old_obj)
        if form.is_valid():
            obj = form.save()
            obj.vendor = user.vendor
            obj.save()
            obj.ingredients.clear()
            for ing in ingredients:
                obj.ingredients.add(Ingredient.objects.get_or_create(name=ing)[0])
            if attachments:
                obj.attachments.all().delete()
                for attach in attachments:
                    ProductAttachment.objects.create(
                        product=obj, file_url=attach.get('file_url'),
                        is_cover=attach.get('is_cover')
                    )
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return VendorProductMutation(
            success=True, message=f"Successfully {'added' if input.get('id') else 'updated'}", instance=obj
        )


class ProductDeleteMutation(graphene.Mutation):
    """
    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_admin_user
    def mutate(self, info, id, **kwargs):
        obj = Product.objects.get(id=id, is_deleted=False)
        obj.is_deleted = True
        obj.deleted_on = timezone.now()
        obj.save()
        return ProductDeleteMutation(
            success=True, message="Successfully deleted"
        )


class Mutation(graphene.ObjectType):
    """
        define all the mutations by identifier name for query
    """
    category_mutation = CategoryMutation.Field()
    category_delete = CategoryDeleteMutation.Field()
    ingredient_mutation = IngredientMutation.Field()
    product_mutation = ProductMutation.Field()
    product_delete = ProductDeleteMutation.Field()
    vendor_product_mutation = VendorProductMutation.Field()
    food_meeting_mutation = FoodMeetingMutation.Field()
    food_meeting_resolve = FoodMeetingResolve.Field()
    food_meeting_delete = MeetingDeleteMutation.Field()
