from unittest import mock

import pytest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django_browserless.auth import authenticators, stores
from django_browserless.entities import AuthToken, PDFRequest
from django_browserless.settings import bl_settings
from rest_framework import permissions, response, status
from rest_framework.views import APIView


@login_required
def dummy_django_view(request):
    return HttpResponse()


@pytest.fixture
def dummy_api_view_class():
    class DummyAPIView(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request):
            return response.Response()

    yield DummyAPIView


@pytest.fixture(autouse=True)
def authenticated_pdf_request():
    stores.CacheStore().set(
        auth_token=AuthToken("test"),
        pdf_request=PDFRequest(url="http://example.com", user_id=1),
    )


@pytest.fixture(autouse=True)
def patch_get_user(monkeypatch):
    monkeypatch.setattr(
        "django_browserless.auth.authenticators.get_user_model", mock.Mock
    )


@pytest.fixture
def authenticated_get_request(rf):
    # Pretend the authentication header was set by browserless
    headers = {bl_settings.AUTH_HEADER_NAME: "test"}
    request = rf.get("", headers=headers)
    # Pretend the request went through the AuthenticationMiddleware
    request.user = AnonymousUser()
    yield request


def test_can_authenticate_against_django_view(
    authenticated_get_request,
):
    """The browserless_authenticated should authenticate a request for a django view
    using the browserless authentication header if present.
    """
    response = dummy_django_view(authenticated_get_request)
    assert response.status_code == status.HTTP_302_FOUND

    response = authenticators.browserless_authenticated(dummy_django_view)(
        authenticated_get_request
    )
    assert response.status_code == status.HTTP_200_OK


def test_can_authenticate_against_django_rest_framework_view(
    authenticated_get_request, dummy_api_view_class
):
    """The BrowserlessAuthentication DRF authentication class should authenticate a
    request for a DRF API using the browserless authentication header if present.
    """
    response = dummy_api_view_class.as_view()(authenticated_get_request)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    dummy_api_view_class.authentication_classes.append(
        authenticators.BrowserlessAuthentication
    )
    response = dummy_api_view_class.as_view()(authenticated_get_request)
    assert response.status_code == status.HTTP_200_OK
