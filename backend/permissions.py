from graphql import GraphQLError

from apps.users.choices import RoleTypeChoices


def is_authenticated(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message='Du er ikke en autorisert bruker.',
                extensions={
                    "message": "Du er ikke en autorisert bruker.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_company_user(func):
    def wrapper(cls, info, **kwargs):
        user = info.context.user
        if not user or not user.company or user.role not in [RoleTypeChoices.COMPANY_OWNER, RoleTypeChoices.COMPANY_MANAGER]:
            raise GraphQLError(
                message='Du er ikke en autorisert bruker.',
                extensions={
                    "message": "Du er ikke en autorisert bruker.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_vendor_user(func):
    def wrapper(cls, info, **kwargs):
        user = info.context.user
        if not user or not user.is_vendor:
            raise GraphQLError(
                message='Du er ikke en autorisert bruker.',
                extensions={
                    "message": "Du er ikke en autorisert bruker.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_super_admin(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message='Du er ikke en autorisert bruker.',
                extensions={
                    "message": "Du er ikke en autorisert bruker.",
                    "code": "unauthorised"
                })
        elif not info.context.user.is_superuser:
            raise GraphQLError(
                message='Du er ikke autorisert til å utføre denne operasjonen.',
                extensions={
                    "message": "Du er ikke autorisert til å utføre denne operasjonen.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_admin_user(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message="Du er ikke en autorisert bruker.",
                extensions={
                    "error": "Du er ikke en autorisert bruker.",
                    "code": "unauthorized"
                }
            )
        if not info.context.user.is_admin:
            raise GraphQLError(
                message="Du er ikke autorisert til å utføre operasjoner.",
                extensions={
                    "error": "Du er ikke autorisert til å utføre operasjoner.",
                    "code": "invalid_permission"
                }
            )
        return func(cls, info, **kwargs)

    return wrapper
