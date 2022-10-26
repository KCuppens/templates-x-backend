import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from graphene_file_upload.django.testing import GraphQLFileUploadTestCase
from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth.models import Group
from apps.company.models import Company
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
        return UserFactory(
            is_staff=True
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_group(self):
        return Group.objects.filter(name="Admin").first()

    def setUp(self):
        self.user = self.create_user()
        self.group = self.create_group()
        print(self.group)
        self.user.groups.add(self.group)
        self.company = self.create_company()
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
        variables = {"id": self.company.id}
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
            "company": self.company.id,
            "access_key": "Test description",
            "secret_key": "Test keywords",
            "bucket_name": "Test keywords",
            "region": "Test keywords",
            "storage_type": "aws",
        }
        response = self.client.execute(mutation, variables)
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
            "company": self.company.id,
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


class UploadFileTestCase(GraphQLFileUploadTestCase):
    fixtures = ["Group.json"]
    
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_company(self):
        return Company.objects.create(
            administrator=self.user,
            name="Test",
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_storage(self):
        return Storage.objects.create(
            company=self.company,
            access_key=settings.AWS_ACCESS_KEY,
            secret_key=settings.AWS_SECRET_KEY,
            bucket_name=settings.AWS_IMAGE_BUCKET,
            region=settings.AWS_REGION,
            is_selected=True,
        )

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def create_user(self):
        return get_user_model().objects.create_user(
            username="test", password="dolphins", is_staff=True
        )

    def setUp(self):
        self.user = self.create_user()
        self.company = self.create_company()
        self.storage = self.create_storage()

    def test_upload_file(self):
        test_file = SimpleUploadedFile("assignment.pdf", b"content")
        response = self.file_query(
            """
            mutation uploadFile($file: Upload!, $id: String!) {
                uploadFile(file: $file, id: $id) {
                    verificationMessage,
                    url
                }
            }
            """,
            op_name="uploadFile",
            files={"file": test_file},
            variables={"id": str(self.company.id)},
        )
        assert response.json()["data"]["uploadFile"]["url"]
        assert (
            response.json()["data"]["uploadFile"]["verificationMessage"]
            == "File uploaded successfully to S3"
        )
