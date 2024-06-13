import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphene_django.forms.types import DjangoFormInputObjectType
from graphql import GraphQLError

# local imports
from apps.bases.utils import (
    camel_case_format,
    raise_graphql_error,
    raise_graphql_error_with_fields,
)
from apps.notifications.tasks import (
    notify_company_order_update,
    send_admin_notification_and_save,
)
from apps.scm.models import Ingredient, Product
from apps.users.choices import RoleTypeChoices
from backend.permissions import is_admin_user, is_authenticated, is_company_user

from .choices import (
    DecisionChoices,
    InvoiceStatusChoices,
    OrderPaymentTypeChoices,
    PaymentTypeChoices,
)
from .forms import (
    BillingAddressForm,
    OrderPaymentForm,
    PaymentMethodForm,
    ProductRatingForm,
)
from .models import (
    AlterCart,
    BillingAddress,
    Order,
    OrderStatus,
    PaymentMethod,
    SellCart,
    UserCart,
)
from .object_types import (
    OrderPaymentType,
    OrderType,
    PaymentMethodType,
    ProductRatingType,
)
from .tasks import add_user_carts, make_previous_payment, notify_user_carts

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


class PaymentMethodDeleteMutation(graphene.Mutation):
    """
    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_authenticated
    def mutate(self, info, id, **kwargs):
        obj = PaymentMethod.objects.get(id=id, is_deleted=False, user=info.context.user)
        obj.is_deleted = True
        obj.deleted_on = timezone.now()
        obj.save()
        return PaymentMethodDeleteMutation(
            success=True, message="Successfully deleted"
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

    @is_authenticated
    def mutate(self, info, item, ingredients, dates):
        user = info.context.user
        if user.role not in [RoleTypeChoices.COMPANY_OWNER, RoleTypeChoices.COMPANY_MANAGER, RoleTypeChoices.COMPANY_EMPLOYEE]:
            raise_graphql_error("User not permitted.")
        item = Product.objects.get(id=item)
        for qt in dates:
            cart, created = SellCart.objects.get_or_create(item=item, added_by=user, date=qt['date'])
            cart.quantity = qt['quantity'] if user.role != RoleTypeChoices.COMPANY_EMPLOYEE else 1
            cart.price = item.actual_price
            cart.price_with_tax = item.price_with_tax
            cart.save()
            cart.ingredients.add(*item.ingredients.filter(id__in=ingredients))
            cart.added_for.clear()
            cart.added_for.add(*User.objects.filter(company=user.company, id__in=qt['added_for']))
        return AddToCart(
            success=True
        )


class RemoveCart(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_company_user
    def mutate(self, info, id, **kwargs):
        user = info.context.user
        carts = user.added_carts.all()
        obj = carts.get(id=id)
        obj.delete()
        return RemoveCart(
            success=True,
            message="Successfully removed",
        )


class EditCartMutation(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()
        quantity = graphene.Int()
        added_for = graphene.List(graphene.ID)

    @is_company_user
    def mutate(self, info, id, quantity, added_for, **kwargs):
        user = info.context.user
        carts = SellCart.objects.filter(Q(added_by=user) | Q(order__company=user.company))
        obj = carts.get(
            Q(order__isnull=True) | Q(order__status__in=[
                InvoiceStatusChoices.PLACED, InvoiceStatusChoices.UPDATED, InvoiceStatusChoices.PAYMENT_PENDING
            ]), id=id
        )
        staffs = User.objects.filter(company=user.company, id__in=added_for)
        if staffs.count() > quantity:
            raise_graphql_error("Quantity is not valid for the added employees.")
        obj.quantity = quantity
        obj.save()
        obj.added_for.clear()
        obj.added_for.add(*staffs)
        add_user_carts.delay(obj.id)
        return EditCartMutation(
            success=True,
            message="Successfully updated",
        )


class SendCartRequest(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    @is_authenticated
    def mutate(self, info, **kwargs):
        user = info.context.user
        carts = user.added_carts.all()
        if not carts.exists():
            raise_graphql_error("No item added.")
        carts.update(is_requested=True)
        return SendCartRequest(
            success=True,
            message="Successfully requested",
        )


class RemoveProductCart(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()

    @is_company_user
    def mutate(self, info, id, **kwargs):
        user = info.context.user
        carts = user.added_carts.all()
        obj = carts.filter(item__id=id)
        obj.delete()
        return RemoveProductCart(
            success=True,
            message="Successfully removed",
        )


class ApproveCart(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(OrderType)

    class Arguments:
        ids = graphene.List(graphene.ID, required=True)

    @is_company_user
    def mutate(self, info, ids, **kwargs):
        user = info.context.user
        carts = SellCart.objects.filter(
            added_by__role=RoleTypeChoices.COMPANY_EMPLOYEE, added_by__company=user.company, id__in=ids,
            is_requested=True
        )
        for qt in carts:
            cart, created = SellCart.objects.get_or_create(item=qt.item, added_by=user, date=qt.date)
            cart.quantity = 1 if created else cart.quantity + 1
            cart.price = qt.item.actual_price
            cart.price_with_tax = qt.item.price_with_tax
            cart.save()
            cart.ingredients.add(*qt.item.ingredients.all())
            cart.added_for.add(qt.added_by)
            qt.delete()
        return ApproveCart(
            success=True,
            message="Successfully removed",
        )


class BillingAddressInput(DjangoFormInputObjectType):
    class Meta:
        form_class = BillingAddressForm


class OrderCreation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        payment_type = graphene.String()
        shipping_address = graphene.ID()
        billing_address = BillingAddressInput()
        company_allowance = graphene.Int()

    @is_company_user
    @transaction.atomic
    def mutate(self, info, payment_type, shipping_address, billing_address, company_allowance=0):
        user = info.context.user
        if payment_type not in OrderPaymentTypeChoices:
            raise_graphql_error("Please select a valid payment-type.")
        carts = user.added_carts.all()
        if not carts.exists():
            raise_graphql_error("Please add carts first.")
        shipping_address = user.company.addresses.get(id=shipping_address)
        billing_form = BillingAddressForm(data=billing_address)
        if not billing_form.is_valid():
            error_data = {}
            for error in billing_form.errors:
                for err in billing_form.errors[error]:
                    error_data[camel_case_format(error)] = err
            raise_graphql_error_with_fields("Invalid input request.", error_data)
        billing_form_data = billing_form.data
        dates = set(list(carts.values_list('date', flat=True)))
        for date in dates:
            obj = Order.objects.create(
                company=user.company, created_by=user, payment_type=payment_type,
                company_allowance=company_allowance, shipping_address=shipping_address,
                delivery_date=date
            )
            billing_form_data['order'] = obj
            BillingAddress.objects.create(**billing_form_data)
            OrderStatus.objects.create(order=obj, status=InvoiceStatusChoices.PLACED)
            date_carts = carts.filter(date=date)
            date_carts.update(added_by=None, order=obj)
            obj.save()
            user.company.invoice_amount += (obj.final_price * company_allowance) / 100
            user.company.ordered_amount += obj.final_price
            user.company.save()
            if payment_type == OrderPaymentTypeChoices.ONLINE:
                OrderStatus.objects.create(order=obj, status=InvoiceStatusChoices.PAYMENT_PENDING)
            notify_user_carts(obj.id)
        send_admin_notification_and_save.delay(
            title="Order placed",
            message="New orders placed "
        )
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
        notify_company_order_update.delay(obj.id)
        return OrderStatusUpdate(
            success=True,
            message="Successfully updated",
        )


class UserCartUpdate(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()
        item = graphene.ID()

    @is_authenticated
    def mutate(self, info, id, item):
        user = info.context.user
        obj = SellCart.objects.get(
            id=id, added_for=user, order__status__in=[
                InvoiceStatusChoices.PLACED, InvoiceStatusChoices.UPDATED, InvoiceStatusChoices.PAYMENT_PENDING
            ]
        )
        product = Product.objects.get(id=item, category=obj.item.category)
        user_cart = UserCart.objects.get(cart=obj, added_for=user)
        AlterCart.objects.get_or_create(
            base=user_cart, cart=obj, item=product
        )
        return UserCartUpdate(
            success=True,
            message="Successfully updated",
        )


class UserCartIngredientUpdate(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()
        ingredients = graphene.List(graphene.ID)

    @is_authenticated
    def mutate(self, info, id, ingredients):
        user = info.context.user
        obj = User.objects.get(
            id=id, added_for=user
        )
        obj.ingredients.clear()
        obj.ingredients.add(*Ingredient.objects.filter(id__in=ingredients))
        return UserCartIngredientUpdate(
            success=True,
            message="Successfully updated",
        )


class ConfirmUserCartUpdate(graphene.Mutation):
    """
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID()
        status = graphene.ID()

    @is_company_user
    def mutate(self, info, id, status):
        user = info.context.user
        obj = AlterCart.objects.get(
            id=id, base__added_for__company=user.company
        )
        if status not in [DecisionChoices.ACCEPTED, DecisionChoices.REJECTED]:
            raise_graphql_error("Invalid action")
        if status == DecisionChoices.ACCEPTED:
            cart, c = SellCart.objects.get_or_create(
                order=obj.previous_cart.order, item=obj.item
            )
            if c:
                cart.price = obj.item.actual_price
                cart.price_with_tax = obj.item.price_with_tax
            else:
                cart.quantity += 1
            cart.save()
            cart.added_for.add(obj.base.added_for)
            obj.previous_cart.added_for.remove(obj.base.added_for)
            obj.previous_cart.cancelled += 1
            obj.previous_cart.save()
            cart.order.save()
            add_user_carts.delay(cart.id)
            OrderStatus.objects.create(order=obj, status=InvoiceStatusChoices.UPDATED)
        return ConfirmUserCartUpdate(
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


class OrderPaymentMutation(DjangoFormMutation):
    """
        update and create new PaymentMethod information by some default fields.
    """
    success = graphene.Boolean()
    message = graphene.String()
    instance = graphene.Field(OrderPaymentType)

    class Meta:
        form_class = OrderPaymentForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = OrderPaymentForm(data=input)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = user
            obj.payment_type = PaymentTypeChoices.CASH
            obj.save()
            make_previous_payment.delay(obj.id)
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
        return OrderPaymentMutation(
            success=True, message="Successfully created", instance=obj
        )


class Mutation(graphene.ObjectType):
    """
        define all the mutations by identifier name for query
    """
    payment_method_mutation = PaymentMethodMutation.Field()
    delete_payment_method = PaymentMethodDeleteMutation.Field()
    order_status_update = OrderStatusUpdate.Field()
    add_product_rating = AddProductRating.Field()

    add_to_cart = AddToCart.Field()
    send_cart_request = SendCartRequest.Field()
    remove_cart = RemoveCart.Field()
    cart_update = EditCartMutation.Field()
    remove_product_cart = RemoveProductCart.Field()
    approve_cart_request = ApproveCart.Field()
    user_cart_update = UserCartUpdate.Field()
    user_cart_ingredients_update = UserCartIngredientUpdate.Field()
    confirm_user_cart_update = ConfirmUserCartUpdate.Field()
    place_order = OrderCreation.Field()
    create_payment = OrderPaymentMutation.Field()
