from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode

from apps.users.tokens import account_activation_token

User = get_user_model()


def decode_token(uidb64, token):
    uid = force_bytes(urlsafe_base64_decode(uidb64)).decode("utf-8")
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        user = None
    check_token = account_activation_token.check_token(user, token)
    return check_token, user
