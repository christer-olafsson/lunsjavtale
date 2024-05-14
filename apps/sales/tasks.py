from django.contrib.auth import get_user_model

from apps.sales.models import Order, SellCart, UserCart

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
            # notify_vendor_product()


@app.task
def add_user_carts(id):
    cart = SellCart.objects.get(id=id)
    for user in cart.added_for.all():
        user_cart, _ = UserCart.objects.get_or_create(added_for=user, cart=cart)
        user_cart.paid_amount = cart.price_with_tax * cart.order.company_allowance / 100
        user_cart.save()
        user_cart.ingredients.add(*cart.ingredients.exclude(id__in=user.allergies.values_list('id', flat=True)))
