
"""All choices for users"""
from django.db import models


class GenderChoices(models.TextChoices):
    """
        define selection choices for gender
    """
    Female = "female"
    Male = "male"
    Other = "other"


class SocialAccountTypeChoices(models.TextChoices):
    """
        define selection choices for social account type
    """
    FACEBOOK = 'facebook'
    LINKEDIN = 'linkedin'
    GOOGLE = 'google'
    APPLE = 'apple'


class DeviceTypeChoices(models.TextChoices):
    """
        define selection choices for device type
    """
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class RoleTypeChoices(models.TextChoices):
    """
        define selection choices for roles
    """
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    OWNER = "owner"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class AgreementChoices(models.TextChoices):
    TERM_AND_CONDITIONS = 'terms-and-conditions'
    PRIVACY_POLICY = 'privacy-policy'
    INSTRUCTION_URL = 'instruction-url'
    ABOUT_US = 'about-us'
