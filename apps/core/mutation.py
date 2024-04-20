import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.forms.types import DjangoFormInputObjectType
from graphql import GraphQLError

# local imports
from apps.bases.utils import (
    camel_case_format,
    get_object_by_id,
    raise_graphql_error_with_fields,
)
from backend.permissions import is_admin_user, is_authenticated

from .forms import (
    AddressTypeForm,
    ContactUsForm,
    FAQCategoryForm,
    FAQForm,
    FollowUsForm,
    LanguageForm,
    PartnerForm,
    PromotionForm,
    SupportedBrandForm,
    ValidAreaForm,
    WhoUAreForm,
)
from .models import (
    FAQ,
    ContactUs,
    FAQCategory,
    FollowUs,
    Language,
    Partner,
    Promotion,
    SupportedBrand,
    TypeOfAddress,
    ValidArea,
    WhoUAre,
    WhoUAreAttachment,
)
from .object_types import (
    ContactUsType,
    FAQCategoryType,
    FAQType,
    FollowUsType,
    LanguageType,
    PartnerType,
    PromotionType,
    SupportedBrandType,
    TypeOfAddressType,
    ValidAreaType,
    WhoUAreType,
)


class ValidAreaMutation(DjangoModelFormMutation):
    """
        Admins can create and update Valid area information through a form input.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(ValidAreaType)

    class Meta:
        form_class = ValidAreaForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        form = ValidAreaForm(data=input)
        if form.data.get('id'):
            obj = get_object_by_id(ValidArea, form.data.get('id'))
            form = ValidAreaForm(data=input, instance=obj)
        if form.is_valid():
            obj, created = ValidArea.objects.update_or_create(id=form.data.get('id'), defaults=form.cleaned_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise_graphql_error_with_fields("Invalid input request.", error_data)
        return ValidAreaMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class AddressTypeMutation(DjangoModelFormMutation):
    """
        Admins can create and update Address Type information through a form input.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(TypeOfAddressType)

    class Meta:
        form_class = AddressTypeForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        form = AddressTypeForm(data=input)
        if form.data.get('id'):
            obj = get_object_by_id(TypeOfAddress, form.data.get('id'))
            form = AddressTypeForm(data=input, instance=obj)
        if form.is_valid():
            obj, created = TypeOfAddress.objects.update_or_create(id=form.data.get('id'), defaults=form.cleaned_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise_graphql_error_with_fields("Invalid input request.", error_data)
        return AddressTypeMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class LanguageMutation(DjangoModelFormMutation):
    """
        Admins can create and update Language information through a form input.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(LanguageType)

    class Meta:
        form_class = LanguageForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        form = LanguageForm(data=input)
        if form.data.get('id'):
            obj = get_object_by_id(Language, form.data.get('id'))
            form = LanguageForm(data=input, instance=obj)
        if form.is_valid():
            obj, created = Language.objects.update_or_create(id=form.data.get('id'), defaults=form.cleaned_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise_graphql_error_with_fields("Invalid input request.", error_data)
        return LanguageMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class FAQCategoryMutation(DjangoModelFormMutation):
    """
        update and create new FAQ Category information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(FAQCategoryType)

    class Meta:
        form_class = FAQCategoryForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = FAQCategoryForm(data=input)
        if form.data.get('id'):
            old_obj = get_object_by_id(FAQCategory, form.data['id'])
            form = FAQCategoryForm(data=input, instance=old_obj)
        if form.is_valid():
            obj, created = FAQCategory.objects.update_or_create(id=form.data.get('id'), defaults=form.cleaned_data)
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
        return FAQCategoryMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class FAQMutation(DjangoModelFormMutation):
    """
        update and create new FAQ information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(FAQType)

    class Meta:
        form_class = FAQForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = FAQForm(data=input)
        if form.data.get('id'):
            old_obj = FAQ.objects.get(id=form.data['id'])
            form = FAQForm(data=input, instance=old_obj)
        if form.is_valid():
            obj, created = FAQ.objects.update_or_create(id=form.data.get('id'), defaults=form.cleaned_data)
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
        return FAQMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class SupportedBrandMutation(DjangoModelFormMutation):
    """
        update and create new SupportedBrand information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(SupportedBrandType)

    class Meta:
        form_class = SupportedBrandForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = SupportedBrandForm(data=input, instance=SupportedBrand.objects.filter(id=input.get('id')).last())
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
        return SupportedBrandMutation(
            success=True, message="Successfully added", instance=obj
        )


class PartnerMutation(DjangoModelFormMutation):
    """
        update and create new Partner information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(PartnerType)

    class Meta:
        form_class = PartnerForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = PartnerForm(data=input, instance=Partner.objects.filter(id=input.get('id')).last())
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
        return PartnerMutation(
            success=True, message="Successfully added", instance=obj
        )


class FollowUsMutation(DjangoModelFormMutation):
    """
        update and create new FollowUs information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(FollowUsType)

    class Meta:
        form_class = FollowUsForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = FollowUsForm(data=input, instance=FollowUs.objects.filter(id=input.get('id')).last())
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
        return FollowUsMutation(
            success=True, message="Successfully added", instance=obj
        )


class PromotionMutation(DjangoModelFormMutation):
    """
        update and create new Promotion information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(PromotionType)

    class Meta:
        form_class = PromotionForm

    def mutate_and_get_payload(self, info, **input):
        form = PromotionForm(data=input, instance=Promotion.objects.filter(id=input.get('id')).last())
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
        return PromotionMutation(
            success=True, message="Successfully added", instance=obj
        )


class ContactUsMutation(DjangoModelFormMutation):
    """
        update and create new ContactUs information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(ContactUsType)

    class Meta:
        form_class = ContactUsForm

    def mutate_and_get_payload(self, info, **input):
        form = ContactUsForm(data=input, instance=ContactUs.objects.filter(id=input.get('id')).last())
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
        return ContactUsMutation(
            success=True, message="Successfully added", instance=obj
        )


class WhoUAreInputObjectType(DjangoFormInputObjectType):

    class Meta:
        form_class = WhoUAreForm


class WhoUAreAttachmentInput(graphene.InputObjectType):
    file_url = graphene.String()
    is_cover = graphene.Boolean()


class WhoUAreMutation(graphene.Mutation):
    """
        update and create new WhoUAre information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(WhoUAreType)

    class Arguments:
        input = WhoUAreInputObjectType()
        attachments = graphene.List(WhoUAreAttachmentInput)

    def mutate(self, info, input, attachments, **kwargs):
        form = WhoUAreForm(data=input, instance=WhoUAre.objects.filter(id=input.get('id')).last())
        if form.is_valid():
            obj = form.save()
            for attachment in attachments:
                WhoUAreAttachment.objects.create(
                    who_u_are=obj, file_url=attachment.get('file_url'), is_cover=attachment.get('is_cover')
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
        return WhoUAreMutation(
            success=True, message="Successfully added", instance=obj
        )


class Mutation(graphene.ObjectType):
    """
        define all the mutations by identifier name for query
    """
    valid_area_mutation = ValidAreaMutation.Field()
    address_type_mutation = AddressTypeMutation.Field()
    language_mutation = LanguageMutation.Field()
    FAQ_category_mutation = FAQCategoryMutation.Field()
    FAQ_mutation = FAQMutation.Field()
    supported_brand_mutation = SupportedBrandMutation.Field()
    partner_mutation = PartnerMutation.Field()
    follow_us_mutation = FollowUsMutation.Field()
    promotion_mutation = PromotionMutation.Field()
    contact_us_mutation = ContactUsMutation.Field()
    who_u_are_mutation = WhoUAreMutation.Field()
