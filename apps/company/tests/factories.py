import factory.fuzzy

from apps.company.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.fuzzy.FuzzyText(length=12)
