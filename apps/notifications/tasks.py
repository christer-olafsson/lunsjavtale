
from logging import getLogger

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.sales.choices import InvoiceStatusChoices
from apps.sales.models import Order, SellCart
from apps.users.choices import DeviceTypeChoices, RoleTypeChoices
from apps.users.models import Company, UserDeviceToken

# local imports
from backend.celery import app
from backend.fcm import ExFCMNotification
from backend.mail import send_direct_mail_by_default_bcc, send_mail_from_template

from .choices import AudienceTypeChoice, NotificationTypeChoice
from .models import Notification, NotificationViewer

User = get_user_model()


@app.task
def notify_company_order_update(id):
    order = Order.objects.get(id=id)
    users = list(order.company.users.filter(
        role__in=[RoleTypeChoices.COMPANY_MANAGER, RoleTypeChoices.COMPANY_OWNER]).values_list('id', flat=True))
    title = "Order status update."
    message = f"Order status was updated to '{str(order.status).replace('-', ' ')}'"
    send_bulk_notification_and_save(
        user_ids=users,
        title=title,
        message=message,
        n_type=NotificationTypeChoice.ORDER_STATUS_CHANGED,
        object_id=order.id
    )
    send_order_update_mail(order.company.working_email, title, message)


@app.task
def send_order_update_mail(email, title, message):
    """
        send mail to user for sell-order update
    """
    body = """
    <html>
    <head></head>
    <body>
    <h3>{0}</h3>
    <p>Thank you for ordering.</p>
    <p>Sincerely,</p>
    <p>Lunsjavtale Team</p>
    </body>
    </html>
    """.format(message)
    send_direct_mail_by_default_bcc(title, body, email)


@app.task
def notify_vendor_product(id):
    cart = SellCart.objects.get(id=id)
    vendor = cart.item.vendor
    if vendor.users.last():
        send_notification_and_save(
            user_id=vendor.users.last().id,
            title="Product added",
            message=f"Company '{cart.order.company.name}' ordered your product -> '{cart.item.name}'",
            n_type=NotificationTypeChoice.VENDOR_PRODUCT_ORDERED,
            object_id=cart.id
        )


@app.task
def notify_company_registration(id):
    company = Company.objects.get(id=id)
    send_admin_notification_and_save(
        title="Company registration",
        message=f"New company '{company.name}' has been registered",
        n_type=NotificationTypeChoice.COMPANY_REGISTERED,
        object_id=company.id
    )


@app.task
def send_notification_and_save(user_id, title, message, n_type, object_id=None):
    user = User.objects.get(id=user_id)
    token = getattr(user, 'device_tokens', None)
    notification = Notification.objects.create(
        # user=instance.sender,
        title=title,
        message=message,
        notification_type=n_type,
        object_id=object_id,
        audience_type=AudienceTypeChoice.USERS
    )
    notification.sent_on = timezone.now()
    notification.save()
    notification.users.add(user)
    token = token.filter(is_current=True).last()
    if token:
        send_user_notification.delay(
            token.device_token, notification.title, notification.message, notification.notification_type)
    else:
        getLogger().error("No user device token found.")


@app.task
def send_bulk_notification_and_save(user_ids, title, message, n_type=NotificationTypeChoice.ALERT, audience_type=AudienceTypeChoice.USERS, object_id=None):
    users = User.objects.filter(id__in=user_ids)
    tokens = list(UserDeviceToken.objects.filter(
        user__in=users).order_by('device_token').values_list('device_token', flat=True).distinct())
    notification = Notification.objects.create(
        # user=instance.sender,
        title=title,
        message=message,
        notification_type=n_type,
        object_id=object_id,
        audience_type=audience_type
    )
    notification.sent_on = timezone.now()
    notification.save()
    notification.users.add(*users)
    if tokens:
        send_bulk_notification(title, message, tokens, n_type)
    else:
        getLogger().error("No user device token found.")


@app.task
def send_admin_notification_and_save(
        title, message, n_type=NotificationTypeChoice.ALERT, audience_type=AudienceTypeChoice.ADMINS, object_id=None
):
    user_tokens = UserDeviceToken.objects.filter(user__is_staff=True, user__is_active=True)
    tokens = list(set(list(user_tokens.values_list('device_token', flat=True).distinct())))
    admins = list(set(list(user_tokens.values_list('user__email').distinct())))
    users = User.objects.filter(email__in=[user[0] for user in admins])
    notification = Notification.objects.create(
        # user=instance.sender,
        title=title,
        message=message,
        notification_type=n_type,
        object_id=object_id,
        audience_type=audience_type
    )
    notification.sent_on = timezone.now()
    notification.save()
    notification.users.add(*users)
    if tokens:
        send_bulk_notification(title, message, tokens, n_type)
    else:
        getLogger().error("No admin device token found.")


@app.task
def send_admin_sell_order_mail(company_id, orders):
    print(100, orders)
    # orders = Order.objects.filter(id__in=orders)
    # print(101, orders)
    company = Company.objects.get(id=company_id)
    send_mail_from_template(
        'admin_sell_order_mail.html', {
            'message': f"New orders placed by '{company.name}'", 'orders': orders
        }, "New Order placed", list(User.objects.filter(
            role__in=[RoleTypeChoices.ADMIN, RoleTypeChoices.SUB_ADMIN]
        ).values_list('email', flat=True))
    )


@app.task
def notify_order_placed(id, orders=[]):
    company = Company.objects.get(id=id)
    title = "Order Placed"
    message = "Your orders have been placed successfully."
    users = list(company.users.filter(
        role__in=[RoleTypeChoices.COMPANY_MANAGER, RoleTypeChoices.COMPANY_OWNER]).values_list('id', flat=True))
    send_bulk_notification_and_save(
        user_ids=users,
        title=title,
        message=message,
        n_type=NotificationTypeChoice.ORDER_PLACED,
        object_id=None
    )
    orders = Order.objects.filter(id__in=orders)
    send_mail_from_template(
        'sell_order_mail.html', {'message': message, 'orders': orders},
        title, company.working_email
    )
    # send_sell_order_mail(company.working_email, title, message, orders)


@app.task
def send_sell_order_mail(email, title, message):
    """
        send mail to user for sell-order update
    """
    body = """
    <html>
    <head></head>
    <body>
    <h3>{0}</h3>
    <p>Thank you for ordering.</p>
    <p>Sincerely,</p>
    <p>Lunsjavtale Team</p>
    </body>
    </html>
    """.format(message)
    send_direct_mail_by_default_bcc(title, body, email)


@app.task
def send_other_mail(email, title, message, link=None):
    """
        send mail to user for advertise update
    """
    if not link:
        link = f"{settings.SITE_URL}"
    body = """
    <html>
    <head></head>
    <body>
    <h3>{0}</h3>
    <p>Please check below link-</p>
    <p><a href='{1}'>{2}</a></p>
    <p>Thank you for staying with us.</p>
    <p>Sincerely,</p>
    <p>Lunsjavtale Team</p>
    </body>
    </html>
    """.format(message, link, link)
    send_direct_mail_by_default_bcc(title, body, email)


@app.task
def send_user_notification(token, title, message, notification_type):
    """
        send notification to single user
    """
    fcm = ExFCMNotification(
        title=title,
        message=message,
        token=token,
        notification_type=notification_type
    )
    try:
        fcm.send_notification()
    except Exception as e:
        getLogger().error(e)


def divide_chunks(ls, n):
    """
        take a list and return the list to n length
    """
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


@app.task
def send_bulk_notification(title, msg, tokens, notification_type):
    """
        divide recipients into chunks for limit 500
    """
    for chunk in divide_chunks(tokens, 500):
        send_chunk_notifications.delay(title, msg, chunk, notification_type)


@app.task
def send_chunk_notifications(title, msg, tokens, notification_type):
    """
        send notification to multiple users by their tokens
    """
    print("Start", timezone.now(), flush=True)
    try:
        ExFCMNotification(title, msg, None, notification_type).send_bulk_notification(tokens)
    except Exception as e:
        print(e)
        getLogger().error(f"{e}")
    print("End", timezone.now(), flush=True)


@app.task
def send_user_bulk_notification(title, message, tokens, notification_type):
    """
        take required arguments and proceed for sending notification
    """
    print(tokens)
    send_bulk_notification(title, message, tokens, notification_type)


@app.task
def send_scheduled_notifications():
    """
        check for notifications if scheduled and not sent
    """
    now = timezone.now()
    start = now.replace(second=0, microsecond=0)
    end = now.replace(second=59)
    notifications = Notification.objects.filter(
        scheduled_on__gte=start, scheduled_on__lte=end, sent_on__isnull=True)
    print(notifications)
    for item in notifications:
        users = item.users.all()
        user_tokens = UserDeviceToken.objects.filter(user__in=users)
        tokens = list(set(list(user_tokens.values_list('device_token', flat=True).distinct())))
        send_user_bulk_notification.delay(item.title, item.message, tokens, item.notification_type)
        item.sent_on = now
        item.save()


@app.task
def send_admin_notification(instance, created):
    user_tokens = UserDeviceToken.objects.filter(user__is_staff=True, user__is_active=True,
                                                 device_type=DeviceTypeChoices.WEB)
    tokens = list(set(list(user_tokens.values_list('device_token', flat=True).distinct())))
    admins = list(set(list(user_tokens.values_list('user__email').distinct())))
    admins = User.objects.filter(email__in=[user[0] for user in admins])
    if admins:
        title = "New order added" if created else "Order updated",
        message = "New order added" if created else "Order updated" + " and waiting for approval.",
        notification_type = NotificationTypeChoice.ORDER_PLACED
        if tokens:
            send_user_bulk_notification(title, message, tokens, notification_type)
        else:
            getLogger().error("No admin device token found.")
    else:
        getLogger().error("No admin found for receiving notification.")


@app.task
def notify_sell_order(instance_id, created):
    """
        send notification to user while order updated
    """
    instance = Order.objects.get(id=instance_id)
    title = None
    message = None
    if instance.status == InvoiceStatusChoices.PLACED:
        title = "Sell order placed"
        message = "Your Sell order was successfully placed."
    elif instance.status not in [
        InvoiceStatusChoices.CANCELLED, InvoiceStatusChoices.ERRORED
    ]:
        title = f"Sell order {instance.status}"
        message = f"Your sell-order was {instance.status}."
    elif instance.status == InvoiceStatusChoices.CANCELLED:
        title = "Sell order cancelled"
        message = f"Your Sell order was cancelled for '{instance.reject_reason}'."
    if instance.status == InvoiceStatusChoices.PLACED:
        send_admin_notification(instance, created)
        send_order_creation_mail(instance_id)
    else:
        send_sell_order_mail(str(instance.id), title, message)
    send_notification_and_save(
        instance.b2b_customer.user.id, title, message, NotificationTypeChoice.ADVERTISE, str(instance.id))


@app.task
def send_order_creation_mail(order_id):
    """
        send mail for account activation
    """
    print("Order created")
    order = Order.objects.get(id=order_id)
    SUBJECT = "Successful order creation"
    # The HTML body of the email.
    body = """
    <html>
    <head></head>
    <body>
      <p>Subject: Your Order {0} has been placed successfully</p>
      <p><b>Lunsjavtale</b></p>
      <p>Dear Valued Customer,</p>
      <p>Thank you for your order! We hope you have enjoyed shopping with us.</p>
      <p>Your order will be delivered within 24 to 48 hours.</p>
      <p>Order number: {0}</p>
      <p>Creation: {1}</p>
      <p>Customer ID: {2}</p>
      <p>Customer name: {3}</p>
      <p>Shipping address: {4}</p>
      <p>Order status: {5}</p>
      <p>Regards,</p>
      <p>Lunsjavtale</p>
    </body>
    </html>
    """.format(
        order.id,
        order.created_on.strftime('%d/%m/%Y %I:%M %p'),
        order.company.id,
        order.company.name,
        order.shipping_address.address,
        "Placed",
    )
    send_direct_mail_by_default_bcc(SUBJECT, body, order.b2b_customer.user.email)


@app.task
def make_seen_all_notifications(user_id):
    user = User.objects.get(id=user_id)
    if user.is_admin:
        notifications = Notification.objects.filter(audience_type=AudienceTypeChoice.ADMINS)
        read = NotificationViewer.objects.filter(notification__in=notifications).values_list('notification', flat=True)
    else:
        notifications = Notification.objects.filter(users=user, sent_on__lte=timezone.now())
        read = NotificationViewer.objects.filter(
            notification__in=notifications, user=user).values_list('notification', flat=True)
    for ins in notifications.exclude(id__in=read):
        obj = NotificationViewer.objects.get_or_create(notification=ins, user=user)[0]
        obj.view_count += 1
        obj.save()
