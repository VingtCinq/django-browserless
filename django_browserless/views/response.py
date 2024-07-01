from __future__ import annotations

from typing import Literal

from django.http import HttpResponse

ContentDisposition = Literal["attachment"] | Literal["inline"]

_CONTENT_TYPE_VALUE = "application/pdf"
_CONTENT_DISPOSITION_HEADER_NAME = "Content-Disposition"
_CONTENT_DISPOSITION_HEADER_VALUE = "{disposition}; filename={filename}"


def get_pdf_response(
    *,
    pdf_content: bytes,
    filename: str,
    content_disposition: ContentDisposition | None = None,
) -> HttpResponse:
    """Build an HTTP response for a pdf content"""
    if not content_disposition:
        content_disposition = "attachment"
    response = HttpResponse(pdf_content, content_type=_CONTENT_TYPE_VALUE)
    response[_CONTENT_DISPOSITION_HEADER_NAME] = (
        _CONTENT_DISPOSITION_HEADER_VALUE.format(
            disposition=content_disposition, filename=filename
        )
    )
    return response
