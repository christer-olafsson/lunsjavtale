import graphene
from django.contrib.auth import get_user_model
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError

# local imports
from apps.bases.utils import camel_case_format
from backend.permissions import is_authenticated, is_company_user

from ..scm.models import Product
from .forms import PaymentMethodForm
from .models import PaymentMethod, SellCart
from .object_types import PaymentMethodType

User = get_user_model()


class PaymentMethodMutation(DjangoModelFormMutation):
    """
        update and create new PaymentMethod information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(PaymentMethodType)

    class Meta:
        form_class = PaymentMethodForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = PaymentMethodForm(data=input)
        object_id = None
        if form.data.get('id'):
            object_id = form.data['id']
            old_obj = PaymentMethod.objects.get(user=user, id=object_id)
            form = PaymentMethodForm(data=input, instance=old_obj)
        form_data = form.data
        if form.is_valid():
            form_data['user'] = user
            obj, created = PaymentMethod.objects.update_or_create(id=object_id, defaults=form_data)
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
        return PaymentMethodMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", instance=obj
        )


class CartInput(graphene.InputObjectType):
    date = graphene.Date()
    quantity = graphene.Int()
    added_for = graphene.List(graphene.ID, required=False)


class AddToCart(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        item = graphene.ID()
        dates = graphene.List(CartInput)

    @is_company_user
    def mutate(self, info, item, dates):
        user = info.context.user
        item = Product.objects.get(id=item)
        for qt in dates:
            cart, created = SellCart.objects.get_or_create(item=item, added_by=user, date=qt['date'])
            cart.quantity = qt['quantity']
            cart.price = item.actual_price
            cart.price_with_tax = item.price_with_tax
            cart.save()
            if qt.get('added_for'):
                cart.added_for.clear()
                cart.added_for.add(*User.objects.filter(company=user.company, id__in=qt['added_for']))
        return AddToCart(
            success=True
        )


class Mutation(graphene.ObjectType):
    """
        define all the mutations by identifier name for query
    """
    payment_method_mutation = PaymentMethodMutation.Field()
