
from django.conf import settings

from backend.celery import app
from backend.mail import send_mail_from_template


@app.task
def send_email_on_delay(template, context, subject, email):
    """
        send or process email by actual template
    """
    print("delay")
    send_mail_from_template(template, context, subject, email)


@app.task
def send_password_reset_mail(email, token):
    """
        send mail including a link for reset password
    """
    print("reset password")
    url = f"{settings.SITE_URL}/password-reset/?email={email}&token={token}"
    SUBJECT = "Reset Password Request"
    send_mail_from_template(
        'apps/users/templates/password_reset_template.html',
        {'url': url},
        SUBJECT, email
    )


@app.task
def send_account_activation_mail(email, username):
    """
        send mail for account activation
    """
    print("account activated")
    SUBJECT = f"Congratulations {username} 🤩"
    send_mail_from_template(
        'apps/users/templates/greeting_from_lunsjavtale.html',
        {'username': username},
        SUBJECT, email
    )
