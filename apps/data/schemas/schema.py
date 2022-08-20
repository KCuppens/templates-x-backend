
import graphene
from graphene_django import DjangoObjectType

from apps.data.models import ConvertAction


class ConvertActionType(DjangoObjectType):
    class Meta:
        model = ConvertAction
        fields = ["from_action", "to_action", "to_action_type"]


class Query(graphene.ObjectType):
    get_convert_actions = graphene.List(
        ConvertActionType, from_action=graphene.String()
    )

    def resolve_get_convert_actions(self, info, from_action, **kwargs):
        return ConvertAction.objects.filter(from_action=from_action)
