import pytest
from apps.company.models import Company
from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth import get_user_model


class CompanyTestCase(GraphQLTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(
            name="Test"
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_administrator(self):
        return get_user_model().objects.create(
            email="test@templatesx.io",
            first_name="test",
            last_name="test"
        )

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_administrator()

    def test_get_company_by_id(self):
        response = self.query(
            """
            query{
                getCompanyById(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.company.id},
        )
        assert response.json()["data"]["id"]

    def test_get_company_by_administrator_id(self):
        response = self.query(
            """
            query{
                getCompanyByAdministratorId(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.administrator.id},
        )
        assert response.json()["data"]["id"]

    def test_create_company(self):
        response = self.file_query(
            """
            mutation createCompany($name: String!) {
                createCompany(name: $name) {
                    id
                }
            }
            """,
            files={"name": "Test company"},
        )
        assert response.json()["data"]["createCompany"]["company"]["id"]

    def test_update_company(self):
        response = self.file_query(
            """
            mutation updateCompany($id: String!, $name: String!) {
                updateCompany(id: $id, name: $name) {
                    id
                }
            }
            """,
            files={"id": self.company.id, "name": "Test company"},
        )
        assert response.json()["data"]["updateCompany"]["company"]["id"]

    def test_delete_company(self):
        response = self.file_query(
            """
            mutation deleteCompany($id: String!) {
                deleteCompany(id: $id) {
                    id
                }
            }
            """,
            files={"id": self.company.id},
        )
        assert response.json()["data"]["deleteCompany"]["message"] == "Company has been deleted."

    def test_invite_user(self):
        response = self.file_query(
            """
            mutation inviteUser($id: String!, $email: String!) {
                inviteUser(id: $id, email: $email) {
                    id
                }
            }
            """,
            files={"id": self.company.id, "email": "test@templatesx.io"},
        )
        assert response.json()["data"]["deleteCompany"]["message"] == "User with test@templatesx.io has been invited to Test."
