from django.contrib.auth import get_user_model

from apps.notifications.tasks import notify_vendor_product
from apps.sales.choices import InvoiceStatusChoices
from apps.sales.models import Order, OrderPayment, SellCart, UserCart

# local imports
from backend.celery import app

User = get_user_model()


@app.task
def notify_user_carts(id):
    obj = Order.objects.get(id=id)
    for cart in obj.order_carts.all():
        add_user_carts(cart.id)
        if cart.item.vendor:
            vendor = cart.item.vendor
            vendor.sold_amount += cart.total_price_with_tax
            vendor.save()
            notify_vendor_product(cart.id)


@app.task
def add_user_carts(id):
    cart = SellCart.objects.get(id=id)
    for user in cart.added_for.all():
        user_cart, c = UserCart.objects.get_or_create(added_for=user, cart=cart)
        if cart.order.statuses.filter(status=InvoiceStatusChoices.PAYMENT_COMPLETED).exists():
            user_cart.paid_amount = cart.price_with_tax * cart.order.company_allowance / 100
            user_cart.save()
        user_cart.ingredients.add(*cart.ingredients.exclude(id__in=user.allergies.values_list('id', flat=True)))
    UserCart.objects.filter(cart=cart).exclude(added_for__in=cart.added_for.all()).delete()


@app.task
def make_previous_payment(id):
    obj = OrderPayment.objects.get(id=id)
    paid_amount = obj.paid_amount
    if obj.payment_for:
        if obj.user_carts.exists():
            for user_cart in obj.user_carts.all().order_by('created_on'):
                if paid_amount > user_cart.cart.price_with_tax - user_cart.paid_amount:
                    user_cart.paid_amount = user_cart.cart.price_with_tax
                    user_cart.save()
                    order = user_cart.cart.order
                    order.paid_amount += user_cart.cart.price_with_tax - user_cart.paid_amount
                    order.save()
                    paid_amount -= user_cart.cart.price_with_tax - user_cart.paid_amount
                else:
                    user_cart.paid_amount += paid_amount
                    user_cart.save()
                    order = user_cart.cart.order
                    order.paid_amount += paid_amount
                    order.save()
                    paid_amount -= paid_amount
                    break
        else:
            user_carts = obj.payment_for.cart_items.all()
            for user_cart in user_carts.order_by('created_on'):
                obj.user_carts.add(user_cart)
                if paid_amount > user_cart.cart.price_with_tax - user_cart.paid_amount:
                    user_cart.paid_amount = user_cart.cart.price_with_tax
                    user_cart.save()
                    order = user_cart.cart.order
                    order.paid_amount += user_cart.cart.price_with_tax - user_cart.paid_amount
                    order.save()
                    paid_amount -= user_cart.cart.price_with_tax - user_cart.paid_amount
                else:
                    user_cart.paid_amount += paid_amount
                    user_cart.save()
                    order = user_cart.cart.order
                    order.paid_amount += paid_amount
                    order.save()
                    paid_amount -= paid_amount
                    break
    else:
        company = obj.company
        company.paid_amount += paid_amount
        company.save()
        if obj.orders.exists():
            for order in obj.orders.all().order_by('created_on'):
                final_price = order.final_price * order.company_allowance / 100
                if paid_amount > final_price - order.paid_amount:
                    order.paid_amount = final_price
                    order.save()
                    paid_amount -= order.final_price - order.paid_amount
                else:
                    order.paid_amount += paid_amount
                    order.save()
                    paid_amount -= paid_amount
                    break
        else:
            orders = obj.company.orders.all()
            for order in orders.order_by('created_on'):
                obj.orders.add(order)
                final_price = order.final_price * order.company_allowance / 100
                if paid_amount > final_price - order.paid_amount:
                    order.paid_amount = final_price
                    order.save()
                    paid_amount -= order.final_price - order.paid_amount
                else:
                    order.paid_amount += paid_amount
                    order.save()
                    paid_amount -= paid_amount
                    break
