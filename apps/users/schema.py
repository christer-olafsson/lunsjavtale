# at backend/users/schema.py
import graphene
from app.users.mutation import Mutation as appMutations
from app.users.query import Query as appQueries


class Query(appQueries, graphene.ObjectType):
    pass


class Mutation(appMutations, graphene.ObjectType):
    pass
