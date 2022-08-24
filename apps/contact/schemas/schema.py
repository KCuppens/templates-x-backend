
import graphene
from graphene_django import DjangoObjectType

from apps.contact.models import Contact


class ContactType(DjangoObjectType):
    class Meta:
        model = Contact
        fields = ["question", "message", "email", "date_created"]


class CreateContact(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        question = graphene.String()
        message = graphene.String()
        email = graphene.String()

    def mutate(self, info, **kwargs):
        question = kwargs.get("question", None)
        message = kwargs.get("message", None)
        email = kwargs.get("email", None)

        if question and message and email:
            Contact.objects.create(question=question, message=message, email=email)
            verification_message = (
                "Thanks for contacting us. We will get back to you ASAP."
            )
        else:
            verification_message = "Please enter all data."
        return CreateContact(verification_message=verification_message)


class Mutation(graphene.ObjectType):
    create_contact = CreateContact.Field()
