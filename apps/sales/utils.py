import requests
from django.conf import settings

from apps.sales.choices import PaymentStatusChoices
from apps.sales.models import OnlinePayment, OrderPayment
from apps.sales.tasks import make_previous_payment


def get_payment_info(payment_id):
    try:
        online_payment = OnlinePayment.objects.get(id=payment_id)
        session_state = online_payment.session_data.get('sessionState')
    except Exception:
        return None
    if session_state == "PaymentSuccessful":
        return online_payment
    elif session_state == "PaymentTerminated":
        return None
    url = f"{settings.PAYMENT_SITE_URL}/checkout/v3/session/{payment_id}/"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Vipps-System-Name": settings.VIPPS_SYSTEM_NAME,
        "Vipps-System-Version": settings.VIPPS_SYSTEM_VERSION,
        "Vipps-System-Plugin-Name": settings.VIPPS_SYSTEM_PLUGIN_NAME,
        "Vipps-System-Plugin-Version": settings.VIPPS_SYSTEM_PLUGIN_VERSION,
        "client_id": settings.VIPPS_CLIENT_ID,
        "client_secret": settings.VIPPS_CLIENT_SECRET,
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Status Code", response.status_code)
        online_payment.session_data = response.json()
        online_payment.save()
        if online_payment.session_data.get('sessionState') == "PaymentTerminated":
            online_payment.order_payment.status = PaymentStatusChoices.CANCELLED
            online_payment.order_payment.save()
        if online_payment.session_data.get('sessionState') == "PaymentSuccessful":
            order_payment = online_payment.order_payment
            order_payment.status = PaymentStatusChoices.COMPLETED
            order_payment.save()
            make_previous_payment(order_payment.id)
    else:
        print("Status Code", response.status_code)
        print("JSON Response ", response.json())
    return online_payment


def make_online_payment(payment_id):
    payment = OrderPayment.objects.get(id=payment_id)
    online_payment = OnlinePayment.objects.create(order_payment=payment)

    url = f"{settings.PAYMENT_SITE_URL}/checkout/v3/session/"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Vipps-System-Name": settings.VIPPS_SYSTEM_NAME,
        "Vipps-System-Version": settings.VIPPS_SYSTEM_VERSION,
        "Vipps-System-Plugin-Name": settings.VIPPS_SYSTEM_PLUGIN_NAME,
        "Vipps-System-Plugin-Version": settings.VIPPS_SYSTEM_PLUGIN_VERSION,
        "client_id": settings.VIPPS_CLIENT_ID,
        "client_secret": settings.VIPPS_CLIENT_SECRET,
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    }
    data = {
        "merchantInfo": {
            "callbackUrl": f"{settings.SITE_URL}/dadmins/?ref={online_payment.id}",
            "returnUrl": f"{settings.SITE_URL}/dadmin/?ref={online_payment.id}",
            "callbackAuthorizationToken": "",
            "termsAndConditionsUrl": f"{settings.SITE_URL}/dadmin"
        },
        "transaction": {
            "amount": {
                "value": int(float(payment.paid_amount) * 100),
                "currency": "NOK"
            },
            "reference": f"{online_payment.id}",
            "paymentDescription": payment.company.name
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("Status Code", response.status_code)
    if response.status_code == 200:
        print("JSON Response ", response.json())
        online_payment.request_headers = headers
        online_payment.request_data = data
        online_payment.response_data = response.json()
        online_payment.save()
        get_payment_info(online_payment.id)  # need to introduce delay function for ten minutes
        if online_payment.response_data.get('checkoutFrontendUrl') and online_payment.response_data.get('token'):
            return f"{online_payment.response_data.get('checkoutFrontendUrl')}?token={online_payment.response_data.get('token')}"
        return None
    else:
        print("Error JSON Response ", response.json())
    return None
