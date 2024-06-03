from django.db import models


class AudienceTypeChoice(models.TextChoices):
    USERS = 'users'
    INACTIVE_USERS = 'inactive-users'
    ADMINS = 'admins'
    CUSTOM = 'custom'
    COMPANY_OWNERS = "company-owners"
    COMPANY_MANAGERS = "company-managers"
    COMPANY_STAFFS = "company-staffs"


class NotificationTypeChoice(models.TextChoices):
    ALERT = 'alert'  # send by admin
    ORDER_STATUS_CHANGED = 'order-status-changed'
    ORDER_PLACED = 'order-placed'
    VENDOR_PRODUCT_ORDERED = 'vendor-product-ordered'
