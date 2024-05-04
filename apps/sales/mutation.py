import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphql import GraphQLError

# local imports
from apps.bases.utils import (
    camel_case_format,
    raise_graphql_error,
    raise_graphql_error_with_fields,
)
from backend.permissions import is_admin_user, is_authenticated, is_company_user

from ..scm.models import Product
from .choices import InvoiceStatusChoices, PaymentTypeChoices
from .forms import PaymentMethodForm, ProductRatingForm
from .models import Order, OrderStatus, PaymentMethod, SellCart
from .object_types import OrderType, PaymentMethodType, ProductRatingType
from .tasks import notify_user_carts

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
        ingredients = graphene.List(graphene.ID)
        dates = graphene.List(CartInput)

    @is_company_user
    def mutate(self, info, item, ingredients, dates):
        user = info.context.user
        item = Product.objects.get(id=item)
        for qt in dates:
            cart, created = SellCart.objects.get_or_create(item=item, added_by=user, date=qt['date'])
            cart.quantity = qt['quantity']
            cart.price = item.actual_price
            cart.price_with_tax = item.price_with_tax
            cart.save()
            cart.ingredients.add(*item.ingredients.filter(id__in=ingredients))
            if qt.get('added_for'):
                cart.added_for.clear()
                cart.added_for.add(*User.objects.filter(company=user.company, id__in=qt['added_for']))
        return AddToCart(
            success=True
        )


class OrderCreation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        coupon = graphene.String()
        payment_type = graphene.String()
        shipping_address = graphene.ID()
        company_allowance = graphene.Int()

    @is_company_user
    @transaction.atomic
    def mutate(self, info, payment_type, shipping_address, coupon="", company_allowance=0):
        user = info.context.user
        if payment_type not in PaymentTypeChoices:
            raise_graphql_error("Please select a valid payment-type.")
        carts = user.added_carts.all()
        if not carts.exists():
            raise_graphql_error("Please add carts first.")

        # ToDo:: need discussion for coupon

        shipping_address = user.company.addresses.get(id=shipping_address)
        dates = list(carts.values_list('date', flat=True))
        for date in dates:
            obj = Order.objects.create(
                company=user.company, created_by=user, payment_type=payment_type,
                company_allowance=company_allowance, shipping_address=shipping_address,
                delivery_date=date
            )
            OrderStatus.objects.create(order=obj, status=InvoiceStatusChoices.PLACED)
            date_carts = carts.filter(date=date)
            date_carts.update(created_by=None, company=user.company)
            obj.actual_price = date_carts.aggregate(tot=Sum('total_price'))['tot'] or 0
            obj.final_price = date_carts.aggregate(tot=Sum('total_price_with_tax'))['tot'] or 0
            obj.save()
            user.company.invoice_amount += (obj.final_price * company_allowance) / 100
            user.company.ordered_amount += obj.final_price
            user.company.save()
            notify_user_carts.delay(obj.id)
        return OrderCreation(
            success=True
        )


class OrderStatusUpdate(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(OrderType)

    class Arguments:
        id = graphene.ID()
        status = graphene.String()

    @is_admin_user
    def mutate(self, info, id, status=""):
        obj = Order.objects.get(id=id)
        if status not in InvoiceStatusChoices:
            raise_graphql_error("Status not valid.")
        OrderStatus.objects.create(order=obj, status=status)
        # notify_company()
        return OrderStatusUpdate(
            success=True,
            message="Successfully updated",
        )


class AddProductRating(DjangoFormMutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(ProductRatingType)

    class Meta:
        form_class = ProductRatingForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = ProductRatingForm(data=input)
        if form.is_valid():
            if not user.cart_items.filter(cart__item=form.cleaned_data['product']).exists():
                raise_graphql_error("User not permitted to rate this product.")
            form.cleaned_data['added_by'] = user
            obj = form.save()
            # notify_admin()
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise_graphql_error_with_fields("Invalid input request.", error_data)
        return AddProductRating(
            success=True,
            message="Successfully added",
            instance=obj
        )


class Mutation(graphene.ObjectType):
    """
        define all the mutations by identifier name for query
    """
    payment_method_mutation = PaymentMethodMutation.Field()
    order_status_update = OrderStatusUpdate.Field()
    add_product_rating = AddProductRating.Field()

    add_to_cart = AddToCart.Field()
    # place_order = OrderCreation.Field()
