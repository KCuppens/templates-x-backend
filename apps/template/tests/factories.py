import factory.fuzzy

from apps.template.models import Template, TemplateCategory


class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Template

    name = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory("apps.company.tests.factories.CompanyFactory")


class TemplateCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TemplateCategory

    name = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory("apps.company.tests.factories.CompanyFactory")
