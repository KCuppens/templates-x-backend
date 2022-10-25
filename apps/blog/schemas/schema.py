import graphene
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import staff_member_required

from apps.blog.models import Blog


class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = "__all__"


class Query(graphene.ObjectType):
    get_filter_blogs = graphene.List(BlogType, name=graphene.String())
    get_blog_detail = graphene.Field(BlogType, id=graphene.String())

    def resolve_get_blog_detail(self, info, id):
        return Blog.objects.filter(id=id).first()

    def resolve_get_filter_blogs(self, info, name=None):
        if name:
            return Blog.objects.filter(name__icontains=name).order_by("-id")
        return Blog.objects.all().order_by("-id")


class CreateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    verification_message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        image = Upload()
        keywords = graphene.String()

    @staff_member_required
    def mutate(self, info, *args, **kwargs):
        name = kwargs.get("name", "")
        description = kwargs.get("description", "")
        image = kwargs.get("image", "")
        keywords = kwargs.get("keywords", "")

        blog = Blog.objects.create(
            name=name,
            description=description,
            image=image,
            keywords=keywords,
        )
        return CreateBlog(
            blog=blog, verification_message="Blog has been created."
        )


class UpdateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        image = Upload()
        keywords = graphene.String()

    @staff_member_required
    def mutate(self, info, *args, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")
        description = kwargs.get("description")
        image = kwargs.get("image")
        keywords = kwargs.get("keywords")

        blog = Blog.objects.filter(id=id).first()
        if blog:
            blog.description = description
            blog.name = name
            blog.image = image
            blog.keywords = keywords
            blog.save(
                update_fields=["description", "name", "image", "keywords"]
            )
            verification_message = "Blog has been updated."
        else:
            verification_message = "Blog doesn't exist."
        return UpdateBlog(
            blog=blog, verification_message=verification_message
        )


class DeleteBlog(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @staff_member_required
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        blog = Blog.objects.filter(id=id).first()
        if blog:
            blog.delete()
            verification_message = "Blog has been deleted."
        else:
            verification_message = "Blog does not exist."
        return DeleteBlog(verification_message=verification_message)


class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()
