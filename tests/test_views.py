import json
from http import HTTPStatus

from django_browserless.views import django_views


def test_cannot_get_pdf_without_providing_a_url_and_filename(rf):
    """An HTTP 400 error must be returned if no url and filename are provided."""
    request = rf.post("", data={})
    response = django_views.url_to_pdf(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert set(json.loads(response.content).keys()) == {"url", "filename"}


def test_can_get_pdf_with_a_url_and_filename(rf, patch_pdf_fetching):
    """Given a valid URL and filename a 200 response should be returned."""
    request = rf.post("", data={"url": "http://example.com", "filename": "hello.pdf"})
    response = django_views.url_to_pdf(request)
    assert response.status_code == HTTPStatus.OK
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"] == "attachment; filename=hello.pdf"


def test_can_choose_pdf_content_disposition(rf, patch_pdf_fetching):
    """The content disposition can be chosen by the client (defaults to attachment)."""
    request = rf.post(
        "",
        data={
            "url": "http://example.com",
            "filename": "hello.pdf",
            "content_disposition": "inline",
        },
    )
    response = django_views.url_to_pdf(request)
    assert response["Content-Disposition"] == "inline; filename=hello.pdf"


def test_browserless_failure_should_return_503(rf, fail_pdf_fetching):
    """A 503 error should be returned in case of a browserless error."""
    request = rf.post("", data={"url": "http://example.com", "filename": "hello.pdf"})
    response = django_views.url_to_pdf(request)
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
