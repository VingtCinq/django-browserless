import logging
import secrets
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils.module_loading import import_string
from rest_framework.authentication import BaseAuthentication

from ..entities import AuthToken
from ..settings import bl_settings

_logger = logging.getLogger(__name__)


def generate_auth_token() -> AuthToken:
    """Generate a random 64 chars value"""
    return AuthToken(secrets.token_hex(32))


class BrowserlessAuthenticationError(Exception):
    pass


def user_from_request(request: HttpRequest) -> AbstractBaseUser:
    auth_token = request.headers.get(bl_settings.AUTH_HEADER_NAME)
    if auth_token is None:
        _logger.warning(
            (
                "Authentication header %s missing in request %s %s."
                " Have you added the browserless_authenticated decorator or the"
                " BrowserlessAuthentication class to your view?"
            ),
            bl_settings.AUTH_HEADER_NAME,
            request.method,
            request.get_full_path(),
        )
        raise BrowserlessAuthenticationError()

    auth_store = import_string(bl_settings.AUTH_STORE)()
    pdf_request = auth_store.get(auth_token)
    if pdf_request is None:
        _logger.warning("Authentication token %s is not/no longer valid", auth_token)
        raise BrowserlessAuthenticationError()

    try:
        return get_user_model().objects.get(pk=pdf_request.user_id)
    except ObjectDoesNotExist:
        _logger.warning("User %s does not exist", pdf_request.user_id)
        raise BrowserlessAuthenticationError()


def browserless_authenticated(view_func):
    @wraps(view_func)
    def wrapper_view(request: HttpRequest, *args, **kwargs):
        if not hasattr(request, "user") or not request.user.is_authenticated:
            try:
                request.user = user_from_request(request)
            except BrowserlessAuthenticationError:
                pass

        return view_func(request, *args, **kwargs)

    return wrapper_view


class BrowserlessAuthentication(BaseAuthentication):
    def authenticate(self, request) -> tuple[AbstractBaseUser, None] | None:
        try:
            user = user_from_request(request)
            return (user, None)
        except BrowserlessAuthenticationError:
            return None
