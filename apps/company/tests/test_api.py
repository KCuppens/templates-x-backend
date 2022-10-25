from unittest import mock

import pytest
from django.contrib.auth.models import Permission
from graphql_jwt.testcases import JSONWebTokenTestCase

from apps.company.tests.factories import CompanyFactory
from apps.users.tests.factories import GroupFactory, UserFactory


class CompanyTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return CompanyFactory()

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_administrator(self):
        return UserFactory(active_company=self.company)

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        group = GroupFactory()
        group.permissions.set(
            [perm.id for perm in Permission.objects.filter()]
        )
        self.administrator.groups.add(group)

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_administrator()
        self.company.administrator = self.administrator
        self.company.save(update_fields=["administrator"])
        self.group = self.create_group()
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
        assert len(response.data["getCompaniesByAdministratorId"]) > 0

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
            query getCompanyFiltered($name: String){
                getCompanyFiltered(name: $name){
                    name,
                    id
                }
            }
            """
        response = self.client.execute(query)
        print(response)
        assert len(response.data) == 1
        assert (
            response.data["getCompanyFiltered"][0]["name"]
            == self.company.name
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
            ==
            "User with test@templatesx.io has been"
            f"invited to {self.company.name}."
        )
