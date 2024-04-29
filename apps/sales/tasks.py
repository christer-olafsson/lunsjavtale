from django.contrib.auth import get_user_model

from apps.sales.models import SellCart, UserCart

# local imports
from backend.celery import app

User = get_user_model()


@app.task
def add_user_carts(id):
    cart = SellCart.objects.get(id=id)
    for user in cart.added_for.all():
        UserCart.objects.get_or_create(added_for=user, cart=cart)
