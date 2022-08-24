from apps.blog.models import Blog
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphene_django_extras import DjangoFilterPaginateListField, LimitOffsetGraphqlPagination
import graphene


class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = ['id', 'name', 'description', 'image', 'keywords']
        filter_fields = [
            "id": ("exact",),
            "name": ("exact", "icontains", "istartswith"),
            "description": ("exact", "icontains", "istartswith"),
            "keywords": ("exact",),
        ]


class Query(graphene.ObjectType):
    get_filter_blogs = DjangoFilterPaginateListField(BlogType, pagination=LimitOffsetGraphqlPagination())
    get_blog_detail = graphene.Field(BlogType, id=graphene.String())

    def resolve_get_blog_detail(self, info, id):
        return Blog.objects.filter(id=id).first()



class CreateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        image = Upload()
        keywords = graphene.String()

    def mutate(self, info, *args, **kwargs):
        name = kwargs.get('name', '')
        description = kwargs.get('description', '')
        image = kwargs.get('image', '')
        keywords = kwargs.get('keywords', '')

        blog = Blog.objects.create(
            name=name,
            description=description,
            image=image,
            keywords=keywords
        )
        return CreateBlog(blog=blog, message="Blog has been created.")


class UpdateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        image = Upload()
        keywords = graphene.String()

    def mutate(self, info, *args, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        description = kwargs.get('description')
        image = kwargs.get('image')
        keywords = kwargs.get('keywords')

        blog = Blog.objects.filter(id=id).first()
        if blog:
            blog.description = description
            blog.name = name
            blog.image = image
            blog.keywords = keywords
            blog.save(update_fields=['description', 'name', 'image', 'keywords'])
            message = "Blog has been updated."
        else:
            message = "Blog doesn\'t exist."
        return UpdateBlog(blog=blog, message=message)


class DeleteBlog(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        blog = Blog.objects.filter(id=id).first()
        if blog:
            blog.delete()
            message = "Blog has been deleted."
        else:
            message = "Blog does not exist."
        return Blog(message=message)


class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()
