from graphene import ObjectType, Schema

from apps.blog.schemas.schema import Query as BlogQuery
from apps.blog.schemas.schema import Mutation as BlogMutation

from apps.company.schemas.schema import Query as CompanyQuery
from apps.company.schemas.schema import Mutation as CompanyMutation

from apps.contact.schemas.schema import Mutation as ContactMutation

from apps.storages.schemas.schema import Query as StorageQuery
from apps.storages.schemas.schema import Mutation as StorageMutation

from apps.template.schemas.schema import Query as TemplateQuery
from apps.template.schemas.schema import Mutation as TemplateMutation

from apps.users.schemas.schema import Query as UserQuery
from apps.users.schemas.schema import Mutation as UserMutation


class Query(
    BlogQuery,
    CompanyQuery,
    StorageQuery,
    TemplateQuery,
    UserQuery,
    ObjectType
):
    pass


class Mutation(
    BlogMutation,
    CompanyMutation,
    ContactMutation,
    StorageMutation,
    TemplateMutation,
    UserMutation,
    ObjectType
):
    pass


schema = Schema(query=Query, mutation=Mutation)
