from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from .. import forms, pdf
from ..client import BrowserlessClientError
from .response import get_pdf_response


@require_POST
def url_to_pdf(request: HttpRequest):
    form = forms.UrlToPdf(request.POST)
    if not form.is_valid():
        return JsonResponse(status=HTTPStatus.BAD_REQUEST, data=form.errors)
    if hasattr(request, "user") and request.user.is_authenticated:
        user_id = request.user.pk
    else:
        user_id = None
    try:
        pdf_content = pdf.from_url(
            url=form.cleaned_data["url"],
            as_user_id=user_id,
            browserless_options=form.cleaned_data.get("browserless_options"),
        )
    except BrowserlessClientError as e:
        return JsonResponse(
            status=HTTPStatus.SERVICE_UNAVAILABLE, data={"error": str(e)}
        )
    response = get_pdf_response(
        pdf_content=pdf_content,
        filename=str(form.cleaned_data.get("filename")),
        content_disposition=form.cleaned_data.get("content_disposition"),
    )
    return response
