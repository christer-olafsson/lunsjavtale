from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.bases.models import BaseWithoutID
from apps.bases.utils import (
    build_absolute_uri,
    create_token,
    email_validator,
    username_validator,
)
from apps.users.choices import DeviceTypeChoices, GenderChoices, RoleTypeChoices
from apps.users.managers import (
    UserAccessTokenManager,
    UserDeviceTokenManager,
    UserManager,
    UserPasswordResetManager,
)
from apps.users.tasks import send_email_on_delay


class ClientDetails(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    slogan = models.TextField(blank=True, null=True)
    social_media_links = models.JSONField(blank=True, null=True)
    logo_url = models.TextField(
        blank=True,
        null=True
    )
    cover_photo_url = models.TextField(
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    formation_date = models.DateField(blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_client_details"  # define table name for database
        verbose_name_plural = 'Client Details'

    def __str__(self) -> str:
        return str(self.name)


class Company(BaseWithoutID):
    name = models.CharField(max_length=256)
    working_email = models.EmailField(max_length=256)
    slogan = models.TextField(blank=True, null=True)
    social_media_links = models.JSONField(blank=True, null=True)
    logo_url = models.TextField(
        blank=True,
        null=True
    )
    cover_photo_url = models.TextField(
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    formation_date = models.DateField(blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_company"  # define table name for database
        verbose_name_plural = 'Companies'

    def __str__(self) -> str:
        return str(self.name)


class User(BaseWithoutID, AbstractBaseUser, PermissionsMixin):
    """Store custom user information.
    all fields are common for all users."""
    username = models.CharField(
        max_length=30,
        validators=[username_validator],
        unique=True,
        null=True
    )  # unique user name to perform username password login.
    email = models.EmailField(
        max_length=100,
        validators=[email_validator],
        unique=True
    )  # unique email to perform email login and send alert mail.
    first_name = models.CharField(
        max_length=150, null=True,
        blank=True
    )
    last_name = models.CharField(
        max_length=150, null=True,
        blank=True
    )
    company = models.ForeignKey(
        to=Company, on_delete=models.DO_NOTHING, related_name='users',
        blank=True, null=True
    )

    # Verification Check
    is_verified = models.BooleanField(
        default=False
    )
    is_email_verified = models.BooleanField(
        default=False
    )
    is_phone_verified = models.BooleanField(
        default=False
    )
    is_profile_photo_verified = models.BooleanField(
        default=False
    )
    rejection_reason_profile_photo = models.TextField(
        blank=True,
        null=True
    )
    term_and_condition_accepted = models.BooleanField(
        default=False
    )
    privacy_policy_accepted = models.BooleanField(
        default=False
    )

    # permission
    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False
    )
    is_superuser = models.BooleanField(
        default=False
    )  # main man of this application.
    is_deleted = models.BooleanField(
        default=False
    )
    deleted_on = models.DateTimeField(
        null=True,
        blank=True
    )
    deleted_phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )

    # details
    last_active_on = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    activation_token = models.UUIDField(
        blank=True,
        null=True
    )
    deactivation_reason = models.TextField(
        null=True,
        blank=True
    )
    is_expired = models.BooleanField(
        default=False
    )  # this flag will define user delete stop this all token for a while

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Enter Phone number with country code"
    )  # phone number validator.
    phone = models.CharField(
        _("phone number"),
        validators=[phone_regex],
        max_length=15,
        unique=True,
        null=True,
        # blank=True
    )
    post_code = models.PositiveIntegerField(
        _("post code"),
        null=True,
        blank=True
    )
    gender = models.CharField(
        max_length=8,
        choices=GenderChoices.choices,
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=16,
        choices=RoleTypeChoices.choices,
        default=RoleTypeChoices.USER
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    # Profile Picture
    photo_url = models.TextField(
        blank=True,
        null=True
    )
    photo_uploaded_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # last login will provide by django abstract_base_user.
    # password also provide by django abstract_base_user.

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = f"{settings.DB_PREFIX}_users"  # define table name for database
        ordering = ['-created_on']  # define default filter as created in descending

    def __str__(self) -> str:
        return str(self.email)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def send_email_verification(self, host):
        self.activation_token = create_token()
        self.is_email_verified = False
        self.save()
        context = {
            'username': self.username,
            'email': self.email,
            'url': build_absolute_uri(f"email-verification/?token={self.activation_token}", host),
        }
        template = 'emails/sing_up_email.html'
        subject = 'Email Verification'
        send_email_on_delay.delay(template, context, subject, self.email)  # will add later for sending verification

    @property
    def is_admin(self) -> bool:
        return self.is_staff or self.is_superuser


class UnitOfHistory(models.Model):
    """We will create log for every action
    those data will store in this model"""

    action = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )  # in this field we will define which action was perform.
    created = models.DateTimeField(
        auto_now_add=True
    )
    old_meta = models.JSONField(
        null=True
    )  # we store data what was the scenario before perform this action.
    new_meta = models.JSONField(
        null=True
    )  # we store data after perform this action.
    header = models.JSONField(
        null=True
    )  # request header that will provide user browser
    # information and others details.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="performer"
    )  # this user will be action performer.
    perform_for = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="perform_for"
    )  # sometime admin/superior  will perform some
    # specific action for employee/or user e.g. payroll change.
    # Generic Foreignkey Configuration. DO NOT CHANGE
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.CharField(
        max_length=100
    )
    content_object = GenericForeignKey()

    class Meta:
        db_table = f"{settings.DB_PREFIX}_unit_of_histories"  # define database table name
        ordering = ['-created']  # define default order as created in descending
        verbose_name_plural = "Unit of histories"

    def __str__(self) -> str:
        return self.action or "action"

    @classmethod
    def user_history(
        cls,
        action,
        user,
        request,
        new_meta=None,
        old_meta=None,
        perform_for=None
    ) -> object:
        try:
            data = {i[0]: i[1] for i in request.META.items() if i[0].startswith('HTTP_')}
        except BaseException:
            data = None
        cls.objects.create(
            action=action,
            user=user,
            old_meta=old_meta,
            new_meta=new_meta,
            header=data,
            perform_for=perform_for,
            content_type=ContentType.objects.get_for_model(User),
            object_id=user.id
        )


class ResetPassword(BaseWithoutID):
    """
    Reset Password will store user data
    who request for reset password.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    token = models.UUIDField()

    objects = UserPasswordResetManager()

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_password_reset"
        ordering = ['-id']  # define default order as id in descending


class UserDeviceToken(BaseWithoutID):
    """
    To Tiggerd FMC notification we need
    device token will store user device token
    to triggered notification.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )
    device_token = models.CharField(
        max_length=200
    )
    device_type = models.CharField(
        max_length=8,
        choices=DeviceTypeChoices.choices
    )
    mac_address = models.CharField(max_length=48, null=True)
    is_current = models.BooleanField(default=False)
    objects = UserDeviceTokenManager()

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_device_tokens"
        ordering = ['-created_on']  # define default order as created in descending

    def save(self, *args, **kwargs):
        super(UserDeviceToken, self).save(*args, **kwargs)
        if self.is_current:
            self.user.device_tokens.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        if UserDeviceToken.objects.filter(device_token=self.device_token):
            UserDeviceToken.objects.filter(device_token=self.device_token).exclude(id=self.id).delete()


class TrackUserLogin(BaseWithoutID):
    username = models.CharField(
        max_length=30, null=True
    )
    email = models.EmailField(
        max_length=100, null=True
    )
    data = models.JSONField(
        null=True
    )  # we store data after perform this action.
    header = models.JSONField(
        null=True
    )  # request header that will provide user browser
    is_success = models.BooleanField(default=False)

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_login_tracks"  # define table name for database
        ordering = ['-created_on']  # define default order as created in descending


class AccessToken(BaseWithoutID):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='access_tokens'
    )
    token = models.TextField()
    mac_address = models.CharField(max_length=48, null=True)

    objects = UserAccessTokenManager()

    class Meta:
        db_table = f"{settings.DB_PREFIX}_access_tokens"  # define table name for database
        ordering = ['-created_on']  # define default order as created in descending


class Address(BaseWithoutID):
    """
        User address information will be stored here by address type.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    address_type = models.ForeignKey('core.TypeOfAddress', on_delete=models.DO_NOTHING)
    address = models.TextField()
    post_code = models.PositiveIntegerField()
    # city = models.ForeignKey('core.City', on_delete=models.SET_NULL, blank=True, null=True)
    # state = models.ForeignKey('core.Region', on_delete=models.SET_NULL, blank=True, null=True)
    # country = models.ForeignKey('core.Country', on_delete=models.SET_NULL, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    full_name = models.CharField(max_length=128, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    instruction = models.TextField(blank=True, null=True)
    default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.address

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_addresses"  # define table name for database
        ordering = ['-id']  # define default order as id in descending
        verbose_name_plural = "Addresses"
        # unique_together = ('user', 'address_type', 'is_deleted')


class UserLanguage(BaseWithoutID):
    """
        User language information will be stored here by address type.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="languages"
    )
    language = models.ForeignKey(to='core.Language', on_delete=models.CASCADE, related_name='users')

    class Meta:
        db_table = f"{settings.DB_PREFIX}_user_languages"  # define table name for database
        ordering = ['-id']  # define default order as id in descending
