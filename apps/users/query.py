# at backend/users/schema.py
import graphene
from django.contrib.auth import get_user_model
from graphene_django.filter import DjangoFilterConnectionField

# local imports
from apps.bases.utils import raise_graphql_error
from backend.permissions import is_admin_user, is_authenticated

from .choices import AgreementChoices, GenderChoices, RoleTypeChoices
from .models import (
    Address,
    Agreement,
    ClientDetails,
    Company,
    Coupon,
    TrackUserLogin,
    UnitOfHistory,
)
from .object_types import (
    AddressType,
    AgreementType,
    ClientDetailsType,
    CompanyType,
    CouponType,
    LogType,
    TrackUserLoginType,
    UserType,
)

User = get_user_model()  # variable taken for User model


class Query(graphene.ObjectType):
    """
        query users information by all users, single user and logged in user
    """
    users = DjangoFilterConnectionField(UserType)
    company_staffs = DjangoFilterConnectionField(UserType)
    user = graphene.Field(UserType, id=graphene.ID())
    me = graphene.Field(UserType)
    logs = DjangoFilterConnectionField(LogType)
    log = graphene.Field(LogType, id=graphene.ID())
    user_login_tracks = DjangoFilterConnectionField(TrackUserLoginType)
    user_login_track = graphene.Field(TrackUserLoginType, id=graphene.ID())
    companies = DjangoFilterConnectionField(CompanyType)
    company = graphene.Field(CompanyType, id=graphene.ID())
    client_details = graphene.Field(ClientDetailsType)
    coupons = DjangoFilterConnectionField(CouponType)
    coupon = graphene.Field(CouponType, id=graphene.ID())
    agreements = DjangoFilterConnectionField(AgreementType)
    agreement = graphene.Field(AgreementType, type_of=graphene.String())
    all_gender_choices = graphene.JSONString()
    addresses = DjangoFilterConnectionField(AddressType)

    @is_authenticated
    def resolve_me(self, info) -> object:
        return info.context.user

    @is_admin_user
    def resolve_users(self, info, **kwargs) -> object:
        return User.objects.all()

    @is_authenticated
    def resolve_company_staffs(self, info, **kwargs) -> object:
        user = info.context.user
        if user.role in [RoleTypeChoices.OWNER, RoleTypeChoices.MANAGER] and user.company:
            return User.objects.filter(company=user.company)
        return User.objects.filter(id=user.id)

    @is_authenticated
    def resolve_user(self, info, id, **kwargs) -> object:
        user = info.context.user
        if user.is_admin:
            users = User.objects.all()
        elif user.role in [RoleTypeChoices.OWNER, RoleTypeChoices.MANAGER] and user.company:
            users = User.objects.filter(company=user.company)
        else:
            users = User.objects.filter(id=user.id)
        return users.filter(id=id).last()

    @is_admin_user
    def resolve_logs(self, info, **kwargs) -> object:
        return UnitOfHistory.objects.all()

    @is_admin_user
    def resolve_log(self, info, id, **kwargs) -> object:
        return UnitOfHistory.objects.filter(id=id).last()

    @is_authenticated
    def resolve_user_login_tracks(self, info, **kwargs) -> object:
        user = info.context.user
        if user.is_admin:
            return TrackUserLogin.objects.all()
        return TrackUserLogin.objects.filter(user=user)

    @is_authenticated
    def resolve_user_login_track(self, info, id, **kwargs) -> object:
        user = info.context.user
        if user.is_admin:
            return TrackUserLogin.objects.filter(id=id).last()
        return TrackUserLogin.objects.filter(user=user, id=id).last()

    @is_authenticated
    def resolve_companies(self, info, **kwargs):
        return Company.objects.all()

    @is_authenticated
    def resolve_company(self, info, id, **kwargs):
        obj = Company.objects.fiter(id=id).last()
        return obj

    def resolve_client_details(self, info, **kwargs):
        client = ClientDetails.objects.last()
        return client

    def resolve_all_gender_choices(self, info, **kwargs):
        return [{"key": c[0], "display": c[1]} for c in GenderChoices.choices]

    def resolve_agreement(self, info, type_of, **kwargs):
        if type_of not in AgreementChoices:
            raise_graphql_error(f"Select a valid choice. '{type_of}' is not one of the available choices.")
        agreement, created = Agreement.objects.get_or_create(type_of=type_of)
        if created:
            agreement.data = "<center><h2>Coming soon...</h2></center>"
            agreement.save()
        return agreement

    @is_admin_user
    def resolve_coupons(self, info, **kwargs) -> object:
        return Coupon.objects.all()

    @is_authenticated
    def resolve_coupon(self, info, id, **kwargs) -> object:
        return Coupon.objects.filter(id=id).last()

    @is_authenticated
    def resolve_addresses(self, info, id, **kwargs) -> object:
        user = info.context.user
        if user.role in [RoleTypeChoices.OWNER, RoleTypeChoices.MANAGER] and user.company:
            return Address.objects.filter(company=user.company)
        return Address.objects.filter(id=None)
