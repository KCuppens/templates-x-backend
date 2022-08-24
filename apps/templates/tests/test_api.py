import pytest
from apps.company.models import Company
from apps.templates.models import Template, TemplateCategory
from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth import get_user_model


class UserTestCase(GraphQLTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(
            name="Test"
        )
    
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_template(self):
        return Template.objects.create(
            name="Test",
            company=self.company
        )
    
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_template_category(self):
        return TemplateCategory.objects.create(
            name="Test",
            company=self.company
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_administrator(self):
        return get_user_model().objects.create(
            email="test@templatesx.io",
            first_name="test",
            last_name="test",
            password="test123"
        )

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_administrator()
        self.template = self.create_template()
        self.template_category = self.create_template_category()

    def test_get_template_by_id(self):
        response = self.query(
            """
            query{
                getTemplateById(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.template.id},
        )
        assert response.json()["data"]["id"]
    
    def test_get_templates_by_administrator_id(self):
        response = self.query(
            """
            query{
                getTemplatesByAdministrator_id(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.administrator.id},
        )
        assert response.json()["data"]["id"]
    
    def test_get_templates(self):
        response = self.query(
            """
            query{
                getTemplates{
                    name,
                    id
                }
            }
            """,
        )
        assert response.json()["data"]["id"]
    
    def test_get_public_templates(self):
        response = self.query(
            """
            query{
                getPublicTemplates{
                    name,
                    id
                }
            }
            """,
        )
        assert response.json()["data"]["id"]
    
    def test_get_template_category_id(self):
        response = self.query(
            """
            query{
                getTemplateCategoryId($id: id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.template_category.id},
        )
        assert response.json()["data"]["id"]
    
    def test_get_template_categories(self):
        response = self.query(
            """
            query{
                getTemplateCategories{
                    name,
                    id
                }
            }
            """,
        )
        assert response.json()["data"]["id"]


    def test_create_template(self):
        response = self.query(
            """
            mutation createTemplate($company: String!, $name: String!, $summary: String, $content_html: String, $content_json: String, $is_active: Boolean, $categories: List) {
                createTemplate(company: $company, name: $name, summary: $summary, content_html: $content_html, content_json: $content_json, is_active: $is_active, categories: $categories) {
                    id
                }
            }
            """,
            variables={"company": "1", "name": "Test", "summary": "Testsum", "content_html": "test123", "content_json": "test123", "is_active": True, "categories": ["1"]},
        )
        assert response.json()["data"]["createTemplate"]["data"]["id"]
    
    def test_update_template(self):
        response = self.query(
            """
            mutation updateTemplate($id: String!, $company: String!, $name: String!, $summary: String, $content_html: String, $content_json: String, $is_active: Boolean, $categories: List) {
                updateTemplate($id: id, company: $company, name: $name, summary: $summary, content_html: $content_html, content_json: $content_json, is_active: $is_active, categories: $categories) {
                    id
                }
            }
            """,
            variables={"id": self.template.id, "company": "1", "name": "Test", "summary": "Testsum", "content_html": "test123", "content_json": "test123", "is_active": True, "categories": ["1"]},
        )
        assert response.json()["data"]["updateTemplate"]["data"]["id"]
    
    def test_delete_template(self):
        response = self.query(
            """
            mutation deleteTemplate($id: String!) {
                deleteTemplate($id: id) {
                    id
                }
            }
            """,
            variables={"id": self.template.id},
        )
        assert response.json()["data"]["updateTemplate"]["verification_message"] == "Template deleted successfully."
    
    def test_activate_template(self):
        response = self.query(
            """
            mutation activateTemplate($id: String!) {
                activateTemplate($id: id) {
                    id
                }
            }
            """,
            variables={"id": self.template.id},
        )
        assert response.json()["data"]["activateTemplate"]["verificationMessage"] == "Template activated successfully."

    def test_make_template_public(self):
        response = self.query(
            """
            mutation makeTemplatePublic($id: String!) {
                makeTemplatePublic($id: id) {
                    id
                }
            }
            """,
            variables={"id": self.template.id},
        )
        assert response.json()["data"]["makeTemplatePublic"]["verificationMessage"] == "Template made public successfully."
    
    def test_approve_public_template(self):
        response = self.query(
            """
            mutation approvePublicTemplate($id: String!) {
                approvePublicTemplate($id: id) {
                    id
                }
            }
            """,
            variables={"id": self.template.id},
        )
        assert response.json()["data"]["approvePublicTemplate"]["verificationMessage"] == "Template approved successfully."
    
    def test_create_template_category(self):
        response = self.query(
            """
            mutation createTemplateCategory($name: String!, $company: String!) {
                createTemplateCategory($name: name, $company: company) {
                    id
                }
            }
            """,
            variables={"name": "Test", "company": self.company.id},
        )
        assert response.json()["data"]["createTemplateCategory"]["id"]
    
    def test_update_template_category(self):
        response = self.query(
            """
            mutation updateTemplateCategory($id: String!, $name: String!, $company: String!) {
                updateTemplateCategory($id: id, $name: name, $company: company) {
                    id
                }
            }
            """,
            variables={"id": self.template_category.id, "name": "Test", "company": self.company.id},
        )
        assert response.json()["data"]["updateTemplateCategory"]["id"]
    
    def test_delete_template_category(self):
        response = self.query(
            """
            mutation deleteTemplateCategory($id: String!) {
                deleteTemplateCategory($id: id) {
                    id
                }
            }
            """,
            variables={"id": self.template_category.id},
        )
        assert response.json()["data"]["deleteTemplateCategory"]["id"]
            
    
    
