import os

import graphene
from django.conf import settings
from django.core.files.storage import default_storage
from google.cloud import storage as google_storage
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required, permission_required

from apps.company.models import Company
from apps.company.permissions import is_company_administrator
from apps.s3.file_handling import init_external_session, upload_file_external
from apps.storages.models import Storage


class StorageType(DjangoObjectType):
    class Meta:
        model = Storage
        fields = "__all__"


class Query(graphene.ObjectType):
    get_company_storages = graphene.List(
        StorageType, id=graphene.String(required=True)
    )

    @login_required
    @permission_required("storages.view_storage")
    def resolve_get_company_storages(self, info, id, **kwargs):
        is_company_administrator(
            info.context.user, Company.objects.filter(id=id).first()
        )
        return Storage.objects.filter(company_id=id)


class CreateStorage(graphene.Mutation):
    storage = graphene.Field(StorageType)
    verification_message = graphene.String()

    class Arguments:
        is_selected = graphene.Boolean()
        storage_type = graphene.String(required=True)

        company = graphene.String(required=True)

        # Google storage
        auth_file = Upload()
        project_id = graphene.String()

        # AWS S3
        access_key = graphene.String()
        secret_key = graphene.String()
        bucket_name = graphene.String()
        region = graphene.String()

    @login_required
    @permission_required("storages.add_storage")
    def mutate(self, info, **kwargs):
        storage_type = kwargs.get("storage_type")
        company = kwargs.get("company")
        is_company_administrator(
            info.context.user, Company.objects.filter(id=company).first()
        )
        is_selected = kwargs.get("is_selected", False)
        if is_selected:
            Storage.objects.filter(company_id=company).update(
                is_selected=False
            )
        if storage_type == "google":
            auth_file = kwargs.get("auth_file")
            project_id = kwargs.get("project_id")
            bucket_name = kwargs.get("bucket_name")
            storage = Storage.objects.create(
                company_id=company,
                is_selected=is_selected,
                storage_type=storage_type,
                auth_file=auth_file,
                project_id=project_id,
                bucket_name=bucket_name,
            )
            verification_message = "Google storage created successfully"
        elif storage_type == "aws":
            access_key = kwargs.get("access_key")
            secret_key = kwargs.get("secret_key")
            bucket_name = kwargs.get("bucket_name")
            region = kwargs.get("region")
            storage = Storage.objects.create(
                company_id=company,
                is_selected=is_selected,
                storage_type=storage_type,
                access_key=access_key,
                secret_key=secret_key,
                bucket_name=bucket_name,
                region=region,
            )
            verification_message = "AWS S3 created successfully"
        else:
            storage = None
            verification_message = "Storage type not found"

        return CreateStorage(
            storage=storage, verification_message=verification_message
        )


class UpdateStorage(graphene.Mutation):
    storage = graphene.Field(StorageType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        is_selected = graphene.Boolean()
        storage_type = graphene.String(required=True)

        company = graphene.String(required=True)

        # Google storage
        auth_file = Upload()
        project_id = graphene.String()

        # AWS S3
        access_key = graphene.String()
        secret_key = graphene.String()
        bucket_name = graphene.String()
        region = graphene.String()

    @login_required
    @permission_required("storages.change_storage")
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        storage_type = kwargs.get("storage_type")
        company = kwargs.get("company")
        is_company_administrator(
            info.context.user, Company.objects.filter(id=company).first()
        )
        is_selected = kwargs.get("is_selected", False)
        if is_selected:
            Storage.objects.filter(company_id=company).update(
                is_selected=False
            )
        storage = Storage.objects.filter(id=id).first()
        if storage and storage_type == "google":
            auth_file = kwargs.get("auth_file")
            project_id = kwargs.get("project_id")
            bucket_name = kwargs.get("bucket_name")
            storage.company_id = company
            storage.is_selected = is_selected
            storage.storage_type = storage_type
            storage.auth_file = auth_file
            storage.project_id = project_id
            storage.bucket_name = bucket_name
            storage.save(
                update_fields=[
                    "company_id",
                    "is_selected",
                    "storage_type",
                    "auth_file",
                    "bucket_name",
                    "project_id",
                ]
            )
            verification_message = "Google storage updated successfully"
        elif storage_type == "aws":
            access_key = kwargs.get("access_key")
            secret_key = kwargs.get("secret_key")
            bucket_name = kwargs.get("bucket_name")
            region = kwargs.get("region")
            storage.company_id = company
            storage.is_selected = is_selected
            storage.storage_type = storage_type
            storage.access_key = access_key
            storage.secret_key = secret_key
            storage.bucket_name = bucket_name
            storage.region = region
            storage.save(
                update_fields=[
                    "company_id",
                    "is_selected",
                    "storage_type",
                    "access_key",
                    "secret_key",
                    "bucket_name",
                    "region",
                ]
            )
            verification_message = "AWS S3 updated successfully"
        else:
            verification_message = "Storage type not found"

        return UpdateStorage(
            storage=storage, verification_message=verification_message
        )


class SelectStorage(graphene.Mutation):
    storage = graphene.Field(StorageType)
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    @permission_required("storages.change_storage")
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        storage = Storage.objects.filter(id=id).first()
        is_company_administrator(info.context.user, storage.company)
        if storage:
            Storage.objects.filter(company_id=storage.company).update(
                is_selected=False
            )

        if storage:
            storage.is_selected = not storage.is_selected
            storage.save(update_fields=["is_selected"])

        return UpdateStorage(
            storage=storage,
            verification_message="Storage (de)selected successfully",
        )


class DeleteStorage(graphene.Mutation):
    verification_message = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    @permission_required("storages.delete_storage")
    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        storage = Storage.objects.filter(id=id).first()
        is_company_administrator(info.context.user, storage.company)
        if storage:
            storage.delete()

        return DeleteStorage(
            verification_message="Storage deleted successfully"
        )


class UploadFile(graphene.Mutation):
    verification_message = graphene.String()
    url = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        file = Upload(required=True)

    def mutate(self, info, **kwargs):
        id = kwargs.get("id")
        company = Company.objects.filter(id=id).first()
        is_company_administrator(info.context.user, company)
        file = kwargs.get("file")
        if company:
            storage = Storage.objects.filter(
                company_id=company, is_selected=True
            ).first()
            if storage.storage_type == "google":
                storage_client = (
                    google_storage.Client.from_service_account_json(
                        storage.auth_file
                    )
                )
                bucket = storage_client.get_bucket(storage.bucket_name)
                blob = bucket.blob(file.name)
                blob.upload_from_filename(file)
                url = blob.public_url
            elif storage.storage_type == "aws":
                session = init_external_session(
                    storage.access_key, storage.secret_key, storage.region
                )
                full_path = (
                    f"{settings.MEDIA_ROOT}{storage.id}/files/{file.name}"
                )
                s3_path = f"/templatesx/{file.name}"
                default_storage.save(full_path, file)
                url = upload_file_external(
                    session, storage.bucket_name, full_path, s3_path
                )
                verification_message = "File uploaded successfully to S3"
            else:
                url = None
                verification_message = "File not uploaded"
            if os.path.exists(file.name):
                os.remove(file.name)
        return UploadFile(url=url, verification_message=verification_message)


class Mutation(graphene.ObjectType):
    create_storage = CreateStorage.Field()
    update_storage = UpdateStorage.Field()
    delete_storage = DeleteStorage.Field()
    select_storage = SelectStorage.Field()
    upload_file = UploadFile.Field()
