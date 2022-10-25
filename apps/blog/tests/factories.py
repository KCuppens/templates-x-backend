import factory.fuzzy

from apps.blog.models import Blog


class BlogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Blog

    name = factory.fuzzy.FuzzyText(length=12)
    description = factory.fuzzy.FuzzyText(length=48)
    keywords = factory.fuzzy.FuzzyText(length=36)
