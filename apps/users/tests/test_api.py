from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.testcases import JSONWebTokenTestCase
from apps.company.tests.factories import CompanyFactory
from apps.users.tests.factories import UserFactory
from apps.company.models import Company
from apps.users.tokens import account_activation_token


class UserTestCase(JSONWebTokenTestCase):
    fixtures = ["Group.json"]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return CompanyFactory()

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return UserFactory(
            is_staff=True,
            company=self.company
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        return Group.objects.filter(name="Admin").first()

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_user()
        self.group = self.create_group()
        self.administrator.groups.add(self.group)
        self.company.administrator = self.administrator
        self.company.save(update_fields=["administrator"])
        self.client.authenticate(self.administrator)

    def test_get_invited_users(self):
        query = """
            query getInvitedUsers($id: String!) {
                getInvitedUsers(id: $id){
                    username
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getInvitedUsers"] == []

    def test_get_company_permission_groups(self):
        query = """
            query getCompanyPermissionGroups($id: String!) {
                getCompanyPermissionGroups(id: $id){
                    name,
                    id
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getCompanyPermissionGroups"] == []

    def test_get_permissions_for_company(self):
        query = """
            query getPermissionsForCompany($id: String!) {
                getPermissionsForCompany(id: $id){
                    name,
                    id
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getPermissionsForCompany"] == []

    @mock.patch("apps.users.schemas.schema.send_email.delay")
    def test_reset_password(self, send_email):
        query = """
            mutation resetPassword($email: String!) {
                resetPassword(email: $email) {
                    verificationMessage
                }
            }
            """
        variables = {"email": self.administrator.email}
        response = self.client.execute(query, variables)
        send_email.assert_called_once()
        assert (
            response.data["resetPassword"]["verificationMessage"]
            == "A password reset link was sent to your email address."
        )

    def test_reset_password_confirm(self):
        token = account_activation_token.make_token(self.administrator)
        uid = urlsafe_base64_encode(force_bytes(self.administrator.pk))
        query = """
            mutation resetPasswordConfirm(
                $uidb64: String!, $token: String!, $password: String!) {
                resetPasswordConfirm(
                    uidb64: $uidb64, token: $token, password: $password) {
                    verificationMessage
                }
            }
            """
        variables = {
            "uidb64": uid,
            "token": token,
            "password": "test12345",
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["resetPasswordConfirm"]["verificationMessage"]
            == "Password has been succesfully resetted."
        )

    def test_create_group(self):
        query = """
            mutation createGroup(
                $company: String!, $name: String!) {
                createGroup(
                    company: $company, name: $name) {
                    verificationMessage
                }
            }
            """
        variables = {
            "company": str(self.company.id),
            "name": "Perm group",
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["createGroup"]["verificationMessage"]
            == "Group is created successfully"
        )

    def test_update_group(self):
        query = """
            mutation updateGroup(
                $id: String!, $name: String!) {
                updateGroup(id: $id, name: $name) {
                    verificationMessage
                }
            }
            """
        variables = {
            "id": str(self.group.id),
            "name": "Perm group",
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["updateGroup"]["verificationMessage"]
            == "Group is updated successfully"
        )

    def test_delete_group(self):
        query = """
            mutation deleteGroup($id: String!) {
                deleteGroup(id: $id) {
                    verificationMessage
                }
            }
            """
        variables = {"id": str(self.group.id)}
        response = self.client.execute(query, variables)
        assert (
            response.data["deleteGroup"]["verificationMessage"]
            == "The group has been deleted."
        )

    def test_add_user_to_group(self):
        query = """
            mutation addUserToGroup(
                $user_id: String!, $group_id: String!) {
                addUserToGroup(userId: $user_id, groupId: $group_id) {
                    verificationMessage
                }
            }
            """
        variables = {
            "group_id": str(self.group.id),
            "user_id": str(self.administrator.id),
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["addUserToGroup"]["verificationMessage"]
            == "The user has been added to the group."
        )

    def test_delete_user_from_group(self):
        query = """
            mutation deleteUserFromGroup(
                $user_id: String!, $group_id: String!) {
                deleteUserFromGroup(userId: $user_id, groupId: $group_id) {
                    verificationMessage
                }
            }
            """
        variables = {
            "group_id": str(self.group.id),
            "user_id": str(self.administrator.id),
        }
        response = self.client.execute(query, variables)
        assert (
            response.data["deleteUserFromGroup"]["verificationMessage"]
            == "The user has been removed from the group!"
        )


class UserAuthTestCase(GraphQLTestCase):
    fixtures = ["Group.json"]
    
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(name="Test")

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return get_user_model().objects.create_user(
            username="test", password="dolphins", is_staff=True
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        return Group.objects.create(name="testgroup")

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_user()
        self.group = self.create_group()

    @mock.patch("apps.users.schemas.schema.send_email.delay")
    def test_register_user(self, send_email):
        response = self.query(
            """
            mutation registerUser(
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!) {
                registerUser(
                    firstName: $first_name,
                    lastName: $last_name,
                    email: $email,
                    password: $password) {
                    user{
                        id
                    },
                    verificationMessage
                }
            }
            """,
            variables={
                "first_name": "Test",
                "last_name": "Test",
                "email": "test@templatesx.io",
                "password": "test123",
            },
        )
        send_email.assert_called_once()
        assert response.json()["data"]["registerUser"]["user"]["id"]
        assert (
            response.json()["data"]["registerUser"]["verificationMessage"]
            == "Successfully created user, Test Test"
        )

    def test_activate_user(self):
        token = account_activation_token.make_token(self.administrator)
        uid = urlsafe_base64_encode(force_bytes(self.administrator.pk))
        response = self.query(
            """
            mutation activateUser($uid: String!, $token: String!) {
                activateUser(uid: $uid, token: $token) {
                    verificationMessage
                }
            }
            """,
            variables={"token": token, "uid": uid},
        )
        assert (
            response.json()["data"]["activateUser"]["verificationMessage"]
            == "The user has been activated."
        )

    def test_login_user(self):
        self.client.logout()
        self.administrator.is_active = True
        self.administrator.save(update_fields=["is_active"])
        response = self.query(
            """
            mutation loginUser($email: String!, $password: String!) {
                loginUser(email: $email, password: $password) {
                    verificationMessage
                }
            }
            """,
            variables={"email": "test", "password": "dolphins"},
        )
        print(response)
        assert (
            response.json()["data"]["loginUser"]["verificationMessage"]
            == "You logged in successfully."
        )
