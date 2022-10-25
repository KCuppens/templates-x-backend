import factory.fuzzy
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.fuzzy.FuzzyText(length=12)
    email = factory.Faker("email")
    password = factory.fuzzy.FuzzyText(length=12)
    active_company = factory.SubFactory(
        "apps.company.tests.factories.CompanyFactory"
    )


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.fuzzy.FuzzyText(length=10)
