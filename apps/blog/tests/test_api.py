import pytest
from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth import get_user_model
from apps.blog.models import Blog


class BlogTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_blog(self):
        return Blog.objects.create(
            name="Test",
            description="Test description",
            keywords="Test keywords"
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return get_user_model().objects.create_user(
            username="test",
            password="dolphins",
            is_staff=True
        )

    def setUp(self):
        self.blog = self.create_blog()
        self.user = self.create_user()
        self.client.authenticate(self.user)

    def test_get_filter_blogs(self):
        query = (
            """
            {
                getFilterBlogs(
                    filter: {
                        or: [
                            {name: {contains: "Test"}}
                        ]
                    }
                    ){
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
            """
        )
        response = self.client.execute(query)
        assert len(response.data) == 1
        assert response.data["getFilterBlogs"]["edges"][0]["node"]["name"] == "Test"

    def test_get_blog_detail(self):
        query = (
            """
            query getBlogDetail($id: String!) {
                getBlogDetail(id: $id){
                    name,
                    id,
                    description,
                    keywords
                }
            }
            """
        )
        variables = {"id": str(self.blog.id)}
        response = self.client.execute(query, variables)
        assert response.data["getBlogDetail"]["name"] == "Test"
        assert response.data["getBlogDetail"]["description"] == "Test description"
        assert response.data["getBlogDetail"]["keywords"] == "Test keywords"

    def test_create_blog(self):
        mutation = (
            """
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
        )
        variables = {
            "name": "Test blog",
            "description": "Test description",
            "keywords": "Test keywords",
        }
        response = self.client.execute(mutation, variables)
        assert response.data["createBlog"]["blog"]["id"]

    def test_update_blog(self):
        mutation = (
            """
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
        )
        variables = {
            "id": str(self.blog.id),
            "name": "Test blog 2",
            "description": "Test description 2",
            "keywords": "Test keywords 2",
        }
        response = self.client.execute(mutation, variables)
        assert response.data["updateBlog"]["blog"]["id"]
        assert response.data["updateBlog"]["blog"]["name"] == "Test blog 2"
        assert (response.data["updateBlog"]["blog"]["description"]
                ==
                "Test description 2")
        assert (response.data["updateBlog"]["blog"]["keywords"]
                ==
                "Test keywords 2")

    def test_delete_blog(self):
        mutation = (
            """
            mutation deleteBlog($id: String!) {
                deleteBlog(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables = {
            "id": str(self.blog.id),
        }
        response = self.client.execute(mutation, variables)
        assert (
            response.data["deleteBlog"]["verificationMessage"]
            ==
            "Blog has been deleted."
        )
