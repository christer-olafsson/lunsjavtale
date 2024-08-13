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
    VENDOR_PRODUCT_ADDED = 'vendor-product-added'
    VENDOR_PRODUCT_UPDATED = 'vendor-product-updated'
    ORDER_PLACED = 'order-placed'
    ORDER_STATUS_CHANGED = 'order-status-changed'
    VENDOR_PRODUCT_ORDERED = 'vendor-product-ordered'
    COMPANY_REGISTERED = 'company-registered'
