from http import HTTPStatus

import pytest
from django_browserless.views import drf_views
from rest_framework.test import APIRequestFactory

pdf_view = drf_views.UrlToPdf.as_view()


@pytest.fixture()
def api_rf():
    yield APIRequestFactory()


def test_cannot_get_pdf_without_providing_a_url_and_filename(api_rf):
    """An HTTP 400 error must be returned if no url and filename are provided."""
    request = api_rf.post("", data={})
    response = pdf_view(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert set(response.data.keys()) == {"url", "filename"}


def test_can_get_pdf_with_a_url_and_filename(api_rf, patch_pdf_fetching):
    """Given a valid URL and filename a 200 response should be returned."""
    request = api_rf.post(
        "", data={"url": "http://example.com", "filename": "hello.pdf"}
    )
    response = pdf_view(request)
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"] == "attachment; filename=hello.pdf"


def test_can_choose_pdf_content_disposition(api_rf, patch_pdf_fetching):
    """The content disposition can be chosen by the client (defaults to attachment)."""
    request = api_rf.post(
        "",
        data={
            "url": "http://example.com",
            "filename": "hello.pdf",
            "content_disposition": "inline",
        },
    )
    response = pdf_view(request)
    assert response["Content-Disposition"] == "inline; filename=hello.pdf"


def test_browserless_failure_should_return_503(api_rf, fail_pdf_fetching):
    """A 503 error should be returned in case of a browserless error."""
    request = api_rf.post(
        "", data={"url": "http://example.com", "filename": "hello.pdf"}
    )
    response = pdf_view(request)
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
