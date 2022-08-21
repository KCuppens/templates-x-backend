import pytest
from apps.company.models import Company
from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth import get_user_model
from apps.users.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import Group

class UserTestCase(GraphQLTestCase):
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
            last_name="test",
            password="test123"
        )
    
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        return Group.objects.create(
            name="testgroup"
        )

    def setUp(self):
        self.company = self.create_company()
        self.administrator = self.create_administrator()
        self.group = self.create_group()

    def test_get_invited_users(self):
        response = self.query(
            """
            query{
                getInvitedUsers(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.company.id},
        )
        assert response.json()["data"]["id"]

    def test_get_company_permission_groups(self):
        response = self.query(
            """
            query{
                getCompanyPermissionGroups(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.company.id},
        )
        assert response.json()["data"]["id"]

    def test_get_permissions_for_company(self):
        response = self.query(
            """
            query{
                getPermissionsForCompany(id: $id){
                    name,
                    id
                }
            }
            """,
            variables={"id": self.company.id},
        )
        assert response.json()["data"]["id"]

    def test_register_user(self):
        response = self.query(
            """
            mutation registerUser($first_name: String!, $last_name: String!, $email: String!, $password: String!) {
                registerUser(first_name: $first_name, last_name: $last_name, email: $email, password: $password) {
                    id
                }
            }
            """,
            variables={"first_name": "Test", "last_name": "Test", "email": "test@templatesx.io", "password": "test123"},
        )
        assert response.json()["data"]["registerUser"]["data"]["user"]["id"]
        assert response.json()["data"]["registerUser"]["data"]["verification_message"] == f"Successfully created user, Test Test"

    def test_activate_user(self):
        token = account_activation_token.make_token(self.administrator)
        uid = urlsafe_base64_encode(force_bytes(self.administrator.pk))
        response = self.query(
            """
            mutation activateUser($uid: String!, token: String!) {
                activateUser(uid: $uid, token: $token) {
                    id
                }
            }
            """,
            variables={"token": token, "uid": uid},
        )
        assert response.json()["data"]["activateUser"]["verification_message"] == "The user has been activated."

    def test_login_user(self):
        self.administrator.is_active = True
        self.administrator.save(update_fields=["is_active"])
        response = self.query(
            """
            mutation loginUser($email: String!, $password: String!) {
                loginUser(email: $email, password: $password) {
                    id
                }
            }
            """,
            variables={"email": "test@templatesx.io", "password": "test123"},
        )
        assert response.json()["data"]["loginUser"]["verification_message"] == "You logged in successfully."

    def test_logout_user(self):
        self.administrator.is_active = True
        self.administrator.save(update_fields=["is_active"])
        response = self.query(
            """
            mutation loginUser($email: String!, $password: String!) {
                loginUser(email: $email, password: $password) {
                    id
                }
            }
            """,
            variables={"email": "test@templatesx.io", "password": "test123"},
        )
        assert response.json()["data"]["loginUser"]["verification_message"] == "You logged in successfully."
        response = self.query(
            """
            mutation logoutUser{
                logoutUser{
                    is_logged_out
                }
            }
            """,
        )
        assert response.json()["data"]["logoutUser"]["is_logged_out"]
        assert response.json()["data"]["logoutUser"]["verification_message"] == 'User successfully logged out!'

    def test_reset_password(self):
        response = self.query(
            """
            mutation resetPassword($email: String!) {
                resetPassword(email: $email) {
                    verificationMessage
                }
            }
            """,
            variables={"email": "test@templatesx.io"},
        )
        assert response.json()["data"]["resetPassword"]["verification_message"] == "A password reset link was sent to your email address."

    def test_reset_password_confirm(self):
        token = account_activation_token.make_token(self.administrator)
        uid = urlsafe_base64_encode(force_bytes(self.administrator.pk))
        response = self.query(
            """
            mutation resetPasswordConfirm($uidb64: String!, $token: String!, $password: String!) {
                resetPasswordConfirm(uidb64: $uidb64, token: $token, password: $password) {
                    verificationMessage
                }
            }
            """,
            variables={"uidb64": uid, "token": token, "password": "test12345"},
        )
        assert response.json()["data"]["resetPasswordConfirm"]["verification_message"] == "Password has been succesfully resetted."

    def test_create_group(self):
        response = self.query(
            """
            mutation createGroup($company: String!, $name: String!, $permission: List) {
                createGroup(company: $company, name: $name, permission: $permission) {
                    verificationMessage
                }
            }
            """,
            variables={"company": self.company.id, "name": "Perm group", "permission": [1,2]},
        )
        assert response.json()["data"]["createGroup"]["verification_message"] == "Group is created successfully"

    def test_update_group(self):
        response = self.query(
            """
            mutation updateGroup($id: String!, $name: String!, $permission: List) {
                updateGroup(id: $id, name: $name, permission: $permission) {
                    verificationMessage
                }
            }
            """,
            variables={"id": self.group.id, "name": "Perm group", "permission": [1,2]},
        )
        assert response.json()["data"]["updateGroup"]["verification_message"] == "Group is updated successfully"

    def test_delete_group(self):
        response = self.query(
            """
            mutation deleteGroup($id: String!) {
                deleteGroup(id: $id) {
                    verificationMessage
                }
            }
            """,
            variables={"id": self.group.id},
        )
        assert response.json()["data"]["deleteGroup"]["verification_message"] == "The group has been deleted."

    def test_add_user_to_group(self):
        response = self.query(
            """
            mutation addUserToGroup($user_id: String!, group_id: String!) {
                addUserToGroup(user_id: $user_id, group_id: $group_id) {
                    verificationMessage
                }
            }
            """,
            variables={"id": self.group.id},
        )
        assert response.json()["data"]["addUserToGroup"]["verification_message"] == "The user has been added to the group."

    def test_delete_user_from_group(self):
        response = self.query(
            """
            mutation deleteUserFromGroup($user_id: String!, group_id: String!) {
                deleteUserFromGroup(user_id: $user_id, group_id: $group_id) {
                    verificationMessage
                }
            }
            """,
            variables={"id": self.group.id},
        )
        assert response.json()["data"]["deleteUserFromGroup"]["verification_message"] == 'The user has been removed from the group!'

