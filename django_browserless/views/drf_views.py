from http import HTTPStatus

from django.http.response import HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import pdf, serializers
from ..client import BrowserlessClientError
from .response import PdfResponse


class UrlToPdf(APIView):
    def post(self, request: Request) -> HttpResponse:
        serializer = serializers.UrlToPdf(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.pk
        else:
            user_id = None
        try:
            pdf_content = pdf.from_url(
                url=serializer.validated_data["url"],
                as_user_id=user_id,
                browserless_options=serializer.validated_data.get(
                    "browserless_options"
                ),
            )
        except BrowserlessClientError as e:
            return Response(
                status=HTTPStatus.SERVICE_UNAVAILABLE, data={"error": str(e)}
            )
        return PdfResponse(
            pdf_content,
            filename=str(serializer.validated_data["filename"]),
            content_disposition=serializer.validated_data.get(
                "content_disposition", "attachment"
            ),
        )
