import pytest
from django.contrib.auth.models import Group
from graphql_jwt.testcases import JSONWebTokenTestCase

from apps.company.tests.factories import CompanyFactory
from apps.storages.models import Storage
from apps.users.tests.factories import UserFactory


class StorageTestCase(JSONWebTokenTestCase):
    fixtures = ["Group.json"]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return CompanyFactory()

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_storage(self):
        return Storage.objects.create(
            company=self.company,
            access_key="Test",
            secret_key="Test description",
            bucket_name="Test keywords",
            region="Test",
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return UserFactory(is_staff=True, company=self.company)

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        return Group.objects.filter(name="Admin").first()

    def setUp(self):
        self.company = self.create_company()
        self.user = self.create_user()
        self.company.administrator = self.user
        self.company.save(update_fields=["administrator"])
        self.group = self.create_group()
        self.user.groups.add(self.group)
        self.storage = self.create_storage()
        self.client.authenticate(self.user)

    def test_get_company_storages(self):
        query = """
            query getCompanyStorages($id: String!) {
                getCompanyStorages(id: $id) {
                    id,
                }
            }
            """
        variables = {"id": str(self.company.id)}
        response = self.client.execute(query, variables)
        assert response.data["getCompanyStorages"][0]["id"]

    def test_create_storage(self):
        mutation = """
            mutation createStorage(
                $company: String!,
                $access_key: String!,
                $secret_key: String!,
                $bucket_name: String!,
                $region: String!,
                $storage_type: String!) {
                createStorage(
                    company: $company,
                    accessKey: $access_key,
                    secretKey: $secret_key,
                    bucketName: $bucket_name,
                    region: $region,
                    storageType: $storage_type) {
                    storage{
                        id
                    }
                }
            }
            """
        variables = {
            "company": str(self.company.id),
            "access_key": "Test description",
            "secret_key": "Test keywords",
            "bucket_name": "Test keywords",
            "region": "Test keywords",
            "storage_type": "aws",
        }
        response = self.client.execute(mutation, variables)
        print(response)
        assert response.data["createStorage"]["storage"]["id"]

    def test_update_storage(self):
        mutation = """
            mutation updateStorage(
                $id: String!,
                $company: String!,
                $access_key: String!,
                $secret_key: String!,
                $bucket_name: String!,
                $region: String!,
                $storage_type: String!) {
                updateStorage(
                    id: $id,
                    company: $company,
                    accessKey: $access_key,
                    secretKey: $secret_key,
                    bucketName: $bucket_name,
                    region: $region,
                    storageType: $storage_type) {
                        storage{
                            id,
                            accessKey
                        }
                }
            }
            """
        variables = {
            "id": str(self.storage.id),
            "company": str(self.company.id),
            "access_key": "Test description",
            "secret_key": "Test keywords",
            "bucket_name": "Test keywords",
            "region": "Test keywords",
            "storage_type": "aws",
        }
        response = self.client.execute(mutation, variables)
        assert response.data["updateStorage"]["storage"]["id"]
        assert (
            response.data["updateStorage"]["storage"]["accessKey"]
            == "Test description"
        )

    def test_delete_storage(self):
        mutation = """
            mutation deleteStorage($id: String!) {
                deleteStorage(id: $id) {
                    verificationMessage
                }
            }
            """
        variables = {
            "id": str(self.storage.id),
        }
        response = self.client.execute(mutation, variables)
        assert (
            response.data["deleteStorage"]["verificationMessage"]
            == "Storage deleted successfully"
        )

    def test_select_storage(self):
        mutation = """
            mutation selectStorage($id: String!) {
                selectStorage(id: $id) {
                    verificationMessage
                }
            }
            """
        variables = {
            "id": str(self.storage.id),
        }
        response = self.client.execute(mutation, variables)
        assert (
            response.data["selectStorage"]["verificationMessage"]
            == "Storage (de)selected successfully"
        )
