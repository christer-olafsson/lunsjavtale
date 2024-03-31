from graphql import GraphQLError


def is_authenticated(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message='You are not authorized user.',
                extensions={
                    "message": "You are not authorized user.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_super_admin(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message='You are not authorized user.',
                extensions={
                    "message": "You are not authorized user.",
                    "code": "unauthorised"
                })
        elif not info.context.user.is_superuser:
            raise GraphQLError(
                message='You are not authorized to perform this operation.',
                extensions={
                    "message": "You are not authorized to perform this operation.",
                    "code": "unauthorised"
                })
        return func(cls, info, **kwargs)
    return wrapper


def is_admin_user(func):
    def wrapper(cls, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(
                message="Unauthorized user!",
                extensions={
                    "error": "You are not authorized user.",
                    "code": "unauthorized"
                }
            )
        if not info.context.user.is_admin:
            raise GraphQLError(
                message="User is not permitted.",
                extensions={
                    "error": "You are not authorized to perform operations.",
                    "code": "invalid_permission"
                }
            )
        return func(cls, info, **kwargs)

    return wrapper
