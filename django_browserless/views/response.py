from __future__ import annotations

from io import BytesIO
from typing import Literal

from django.http import FileResponse

ContentDisposition = Literal["attachment"] | Literal["inline"]

_PDF_CONTENT_TYPE = "application/pdf"


class PdfResponse(FileResponse):
    def __init__(
        self,
        pdf_content: bytes,
        filename: str,
        content_disposition: ContentDisposition,
    ) -> None:
        as_attachment = content_disposition == "attachment"
        super().__init__(
            # A file-like object must be passed for the content disposition header to
            # be automatically set.
            BytesIO(pdf_content),
            filename=filename,
            content_type=_PDF_CONTENT_TYPE,
            as_attachment=as_attachment,
        )
