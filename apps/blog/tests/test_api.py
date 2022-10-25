import pytest
from django.contrib.auth.models import Permission
from graphql_jwt.testcases import JSONWebTokenTestCase

from apps.blog.tests.factories import BlogFactory
from apps.users.tests.factories import GroupFactory, UserFactory


class BlogTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_blog(self):
        return BlogFactory()

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return UserFactory(is_staff=True)

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        group = GroupFactory()
        group.permissions.set(
            [perm.id for perm in Permission.objects.filter()]
        )
        self.user.groups.add(group)

    def setUp(self):
        self.blog = self.create_blog()
        self.user = self.create_user()
        self.group = self.create_group()
        self.client.authenticate(self.user)

    def test_get_filter_blogs(self):
        query = """
            query getFilterBlogs($name: String!) {
                getFilterBlogs(name: $name){
                    name,
                    id,
                    description,
                    keywords
                }
            }
            """
        variables = {"name": self.blog.name}
        response = self.client.execute(query, variables)
        assert len(response.data) == 1
        assert response.data["getFilterBlogs"][0]["name"] == self.blog.name

    def test_get_blog_detail(self):
        query = """
            query getBlogDetail($id: String!) {
                getBlogDetail(id: $id){
                    name,
                    id,
                    description,
                    keywords
                }
            }
            """
        variables = {"id": str(self.blog.id)}
        response = self.client.execute(query, variables)
        assert response.data["getBlogDetail"]["name"] == self.blog.name
        assert (
            response.data["getBlogDetail"]["description"]
            == self.blog.description
        )
        assert (
            response.data["getBlogDetail"]["keywords"] == self.blog.keywords
        )

    def test_create_blog(self):
        mutation = """
            mutation createBlog(
                $name: String!,
                $description: String!,
                $keywords: String!) {
                createBlog(
                    name: $name,
                    description: $description,
                    keywords: $keywords) {
                    blog{
                        id,
                        name,
                        description,
                        keywords
                    }
                }
            }
            """
        variables = {
            "name": "Test blog",
            "description": "Test description",
            "keywords": "Test keywords",
        }
        response = self.client.execute(mutation, variables)
        assert response.data["createBlog"]["blog"]["id"]

    def test_update_blog(self):
        mutation = """
            mutation updateBlog(
                $id: String!,
                $name: String!,
                $description: String!,
                $keywords: String!) {
                updateBlog(
                    id : $id
                    name: $name,
                    description: $description,
                    keywords: $keywords) {
                        blog{
                            id,
                            name,
                            description,
                            keywords
                        }
                }
            }
            """
        variables = {
            "id": str(self.blog.id),
            "name": "Test blog 2",
            "description": "Test description 2",
            "keywords": "Test keywords 2",
        }
        response = self.client.execute(mutation, variables)
        assert response.data["updateBlog"]["blog"]["id"]
        assert response.data["updateBlog"]["blog"]["name"] == "Test blog 2"
        assert (
            response.data["updateBlog"]["blog"]["description"]
            == "Test description 2"
        )
        assert (
            response.data["updateBlog"]["blog"]["keywords"]
            == "Test keywords 2"
        )

    def test_delete_blog(self):
        mutation = """
            mutation deleteBlog($id: String!) {
                deleteBlog(id: $id) {
                    verificationMessage
                }
            }
            """
        variables = {
            "id": str(self.blog.id),
        }
        response = self.client.execute(mutation, variables)
        assert (
            response.data["deleteBlog"]["verificationMessage"]
            == "Blog has been deleted."
        )
