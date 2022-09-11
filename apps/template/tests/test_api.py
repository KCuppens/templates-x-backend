import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from apps.company.models import Company
from apps.template.models import Template, TemplateCategory


class TemplateTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(
            name="Test",
            administrator=self.user
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_template(self):
        return Template.objects.create(
            name="Test",
            company=self.company,
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_template_category(self):
        return TemplateCategory.objects.create(name="Test", company=self.company)

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return get_user_model().objects.create_user(
            username="test",
            password="dolphins",
            is_staff=True
        )

    def setUp(self):
        self.user = self.create_user()
        self.company = self.create_company()
        self.template = self.create_template()
        self.template_category = self.create_template_category()
        self.client.authenticate(self.user)

    def test_get_template_by_id(self):
        query = (
            """
            query getTemplateById($id: String!){
                getTemplateById(id: $id){
                    name,
                    id
                }
            }
            """
        )
        variables = {"id": str(self.template.id)}
        response = self.client.execute(query, variables)
        assert response.data["getTemplateById"]["id"]

    def test_get_templates_by_administrator_id(self):
        self.client.authenticate(self.user)
        query = (
            """
            query {
                getTemplatesByAdministratorId{
                    name
                }
            }
            """
        )
        response = self.client.execute(query)
        assert response.data["getTemplatesByAdministratorId"][0]["name"] == "Test"

    def test_get_templates(self):
        query = (
            """
            query{
                getTemplates{
                    name
                }
            }
            """
        )
        response = self.client.execute(query)
        assert response.data["getTemplates"][0]["name"] == "Test"

    def test_get_public_templates(self):
        query = (
            """
            query{
                getPublicTemplates{
                    name
                }
            }
            """
        )
        response = self.client.execute(query)
        assert response.data["getPublicTemplates"] == []

    def test_get_template_category_id(self):
        query = (
            """
            query getTemplateCategoryId($id: String!){
                getTemplateCategoryId(id: $id){
                    name,
                    id
                }
            }
            """
        )
        variables = {"id": str(self.template_category.id)}
        response = self.client.execute(query, variables)
        assert response.data["getTemplateCategoryId"]["id"]

    def test_get_template_categories(self):
        query = (
            """
            query getTemplateCategories($id: String!){
                getTemplateCategories(id: $id){
                    name
                }
            }
            """
        )
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getTemplateCategories"][0]["name"] == "Test"

    def test_create_template(self):
        query = (
            """
            mutation createTemplate(
                $company: String!,
                $name: String!,
                $summary: String,
                $content_html: String,
                $content_json: String,
                $is_active: Boolean,
                $categories: [String]) {
                createTemplate(
                    company: $company,
                    name: $name,
                    summary: $summary,
                    contentHtml: $content_html,
                    contentJson: $content_json,
                    isActive: $is_active,
                    categories: $categories) {
                        template{
                            id,
                            categories{
                                name
                            }
                        }
                }
            }
            """
        )
        variables = {
            "company": str(self.company.id),
            "name": "Test",
            "summary": "Testsum",
            "content_html": "test123",
            "content_json": "test123",
            "is_active": True,
            "categories": [str(self.template_category.id), ],
        }
        response = self.client.execute(query, variables)
        assert response.data["createTemplate"]["template"]["id"]
        assert response.data["createTemplate"]["template"]["categories"][0]["name"] == "Test"

    def test_update_template(self):
        query = (
            """
            mutation updateTemplate(
                $id: String!,
                $company: String!,
                $name: String!,
                $summary: String,
                $content_html: String,
                $content_json: String,
                $is_active: Boolean,
                $categories: [String]) {
                updateTemplate(
                    id: $id,
                    company: $company,
                    name: $name,
                    summary: $summary,
                    contentHtml: $content_html,
                    contentJson: $content_json,
                    isActive: $is_active,
                    categories: $categories) {
                        template{
                            id
                            categories{
                                name
                            }
                        }
                }
            }
            """
        )
        variables = {
            "id": str(self.template.id),
            "company": str(self.company.id),
            "name": "Test",
            "summary": "Testsum",
            "content_html": "test123",
            "content_json": "test123",
            "is_active": True,
            "categories": [str(self.template_category.id), ],
        }
        response = self.client.execute(query, variables)
        assert response.data["updateTemplate"]["template"]["id"]
        assert response.data["updateTemplate"]["template"]["categories"][0]["name"] == "Test"

    def test_delete_template(self):
        query = (
            """
            mutation deleteTemplate($id: String!) {
                deleteTemplate(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables = {"id": str(self.template.id)}
        response = self.client.execute(query, variables)
        assert (
            response.data["deleteTemplate"]["verificationMessage"]
            == "Template deleted successfully."
        )

    def test_activate_template(self):
        query = (
            """
            mutation activateTemplate($id: String!) {
                activateTemplate(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables={"id": str(self.template.id)}
        response = self.client.execute(query, variables)
        assert (
            response.data["activateTemplate"]["verificationMessage"]
            == "Template activated successfully."
        )

    def test_make_template_public(self):
        query = (
            """
            mutation makeTemplatePublic($id: String!) {
                makeTemplatePublic(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables={"id": str(self.template.id)}
        response = self.client.execute(query, variables)
        assert (
            response.data["makeTemplatePublic"]["verificationMessage"]
            == "Template made public successfully."
        )

    def test_approve_public_template(self):
        query = (
            """
            mutation approvePublicTemplate($id: String!) {
                approvePublicTemplate(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables={"id": str(self.template.id)}
        response = self.client.execute(query, variables)
        assert (
            response.data["approvePublicTemplate"]["verificationMessage"]
            == "Template approved successfully."
        )

    def test_create_template_category(self):
        query = (
            """
            mutation createTemplateCategory(
                $name: String!, $company: String!) {
                createTemplateCategory(name: $name, company: $company) {
                    templateCategory {
                        id
                    }
                }
            }
            """
        )
        variables={"name": "Test", "company": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["createTemplateCategory"]["templateCategory"]["id"]

    def test_update_template_category(self):
        query = (
            """
            mutation updateTemplateCategory(
                $id: String!,
                $name: String!,
                $company: String!) {
                updateTemplateCategory(
                    id: $id,
                    name: $name,
                    company: $company) {
                    templateCategory{
                        id
                    }
                }
            }
            """
        )
        variables = {
            "id": str(self.template_category.id),
            "name": "Test",
            "company": str(self.company.id),
        }
        response = self.client.execute(query, variables)
        assert response.data["updateTemplateCategory"]["templateCategory"]["id"]

    def test_delete_template_category(self):
        query = (
            """
            mutation deleteTemplateCategory($id: String!) {
                deleteTemplateCategory(id: $id) {
                    verificationMessage
                }
            }
            """
        )
        variables={"id": str(self.template_category.id)}
        response = self.client.execute(query, variables)
        assert response.data["deleteTemplateCategory"]["verificationMessage"] == "Template category deleted successfully."
    
    def test_batch_delete_template(self):
        query = (
            """
            mutation batchDeleteTemplate($objects: [String!]!) {
                batchDeleteTemplate(objects: $objects) {
                    verificationMessage
                }
            }
            """
        )
        variables={"objects": [str(self.template.id),]}
        response = self.client.execute(query, variables)
        assert response.data["batchDeleteTemplate"]["verificationMessage"] == "Templates in batch deleted."
