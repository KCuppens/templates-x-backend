import mimetypes

from django.conf import settings


def get_mimetype(filepath):
    return mimetypes.MimeTypes().guess_type(filepath)[0]


def get_initial_file():
    return settings.MEDIA_ROOT + "initial_files/"


def get_conversion_file():
    return settings.MEDIA_ROOT + "conversion_files/"


def get_filename(filepath):
    return filepath.split("/")[-1]
