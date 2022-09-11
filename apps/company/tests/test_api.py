from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from apps.company.models import Company


class CompanyTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(name="Test")

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_administrator(self):
        return get_user_model().objects.create_user(
            username="test@templatesx.io",
            email="test@templatesx.io",
            first_name="test",
            last_name="test",
            is_superuser=False,
            active_company=self.company.id,
        )

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_administrator()
        self.client.authenticate(self.administrator)

    def test_get_company_by_id(self):
        query = """
            query getCompanyById($id: String!){
                getCompanyById(id: $id){
                    name,
                    id
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getCompanyById"]["id"]

    def test_get_company_by_administrator_id(self):
        query = """
            query getCompaniesByAdministratorId($id: String!){
                getCompaniesByAdministratorId(id: $id){
                    name,
                    id
                }
            }
            """
        variables = {"id": str(self.administrator.id)}
        response = self.client.execute(query, variables)
        assert response.data["getCompaniesByAdministratorId"] == []

    def test_get_company_by_user_id(self):
        query = """
            query getCompaniesByUserId($id: String!){
                getCompaniesByUserId(id: $id){
                    name,
                    id
                }
            }
            """
        variables = {"id": str(self.administrator.id)}
        response = self.client.execute(query, variables)
        assert response.data["getCompaniesByUserId"] == []

    def test_get_company_filtered(self):
        query = """
            {
                getCompanyFiltered(
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
        response = self.client.execute(query)
        assert len(response.data) == 1
        assert (
            response.data["getCompanyFiltered"]["edges"][0]["node"]["name"]
            == "Test"
        )

    def test_create_company(self):
        mutation = """
            mutation createCompany($name: String!) {
                createCompany(name: $name) {
                    company{
                        id
                    }
                }
            }
            """
        variables = {"name": "Test company"}
        response = self.client.execute(mutation, variables)
        assert response.data["createCompany"]["company"]["id"]

    def test_update_company(self):
        mutation = """
            mutation updateCompany($id: String!, $name: String!) {
                updateCompany(id: $id, name: $name) {
                    company{
                        id
                    }
                }
            }
            """
        variables = {"id": str(self.company.id), "name": "Test company"}
        response = self.client.execute(mutation, variables)
        assert response.data["updateCompany"]["company"]["id"]

    def test_delete_company(self):
        mutation = """
            mutation deleteCompany($id: String!) {
                deleteCompany(id: $id) {
                    verificationMessage
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(mutation, variables)
        assert (
            response.data["deleteCompany"]["verificationMessage"]
            == "Company has been deleted."
        )

    @mock.patch(
        "apps.company.schemas.schema.send_email.delay",
    )
    def test_invite_user(self, send_email):
        mutation = """
            mutation inviteUser($id: String!, $email: String!) {
                inviteUser(id: $id, email: $email) {
                    verificationMessage
                }
            }
            """
        variables = {
            "id": str(self.company.id),
            "email": "test@templatesx.io",
        }
        response = self.client.execute(mutation, variables)
        send_email.assert_called_once()
        assert (
            response.data["inviteUser"]["verificationMessage"]
            == "User with test@templatesx.io has been invited to Test."
        )
