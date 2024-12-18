from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from django_browserless.views.response import PdfResponse

from .. import forms, pdf
from ..client import BrowserlessClientError


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
    return PdfResponse(
        pdf_content,
        filename=str(form.cleaned_data["filename"]),
        content_disposition=(
            form.cleaned_data.get("content_disposition") or "attachment"
        ),
    )
