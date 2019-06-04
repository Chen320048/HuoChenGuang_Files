from django.contrib.auth.backends import ModelBackend

from apps.account.models import User
from tokens import token_generator

class TokenBackend(ModelBackend):
    def authenticate(self, pk, token):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

        #TOKEN_CHECK_ACTIVE_USER = getattr(settings, "TOKEN_CHECK_ACTIVE_USER", False)

        #if TOKEN_CHECK_ACTIVE_USER and not user.is_active:
        #    return None

        if token_generator.check_token(user,
            token):
            return user
        return None


class LoginBackend(ModelBackend):
    def authenticate(self, username, password,type):
        try:
            user = User.objects.get(username=username,type=type)
            if not user.check_password(password):
                return None
        except User.DoesNotExist:
            return None

        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None

