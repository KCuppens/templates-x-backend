import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def init_external_session(access_key, secret_key, region):
    return boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def init_session():
    return boto3.session.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION,
    )


def create_bucket(bucket_name, region=None, acl="public-read"):
    session = init_session()
    s3_resource = session.resource("s3")
    return s3_resource.create_bucket(Bucket=bucket_name, ACL=acl)


def upload_file(bucket_name, path, object_name):
    session = init_session()
    s3_resource = session.resource("s3")
    if object_name:
        original_path = object_name
    else:
        original_path = path
    if original_path.startswith("/"):
        original_path = original_path[1:]
    bucket = s3_resource.Bucket(bucket_name)
    bucket.upload_file(
        Filename=path, Key=original_path, ExtraArgs={"ACL": "public-read"}
    )

    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{original_path}"
    return s3_url


def upload_file_external(session, bucket_name, path, object_name):
    s3_resource = session.resource("s3")
    if object_name:
        original_path = object_name
    else:
        original_path = path
    if original_path.startswith("/"):
        original_path = original_path[1:]
    bucket = s3_resource.Bucket(bucket_name)
    bucket.upload_file(
        Filename=path, Key=original_path, ExtraArgs={"ACL": "public-read"}
    )

    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{original_path}"
    return s3_url


def download_file(bucket_name, key, path):
    session = init_session()
    s3_resource = session.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    bucket.download_file(Key=key, Filename=path)


def get_file_size(bucket_name, key):
    session = init_session()
    s3_resource = session.resource("s3")
    try:
        return s3_resource.Bucket(bucket_name).Object(key).content_length
    except ClientError:
        return ""


def delete_object(bucket_name, key):
    session = init_session()
    s3_resource = session.resource("s3")
    obj = s3_resource.Object(bucket_name, key)
    obj.delete()


def object_exists(bucket_name, key):
    session = init_session()
    s3_resource = session.resource("s3")
    try:
        s3_resource.Object(bucket_name, key).get()
        return True
    except ClientError:
        return False
