from __future__ import annotations

from typing import Any

from django.utils.module_loading import import_string

from . import client
from .auth.authenticators import generate_auth_token
from .entities import PDFRequest
from .settings import bl_settings


def from_url(
    url: str,
    as_user_id: Any = None,
    browserless_options: dict | None = None,
) -> bytes:
    if as_user_id is not None:
        auth_timeout = bl_settings.DEFAULT_AUTH_TIMEOUT
        auth_store = import_string(bl_settings.AUTH_STORE)()
        auth_token = generate_auth_token()
        auth_store.set(
            auth_token=auth_token,
            pdf_request=PDFRequest(url=url, user_id=as_user_id),
            timeout=auth_timeout,
        )
    else:
        auth_token = None
    return client.fetch_pdf(url=url, auth_token=auth_token, options=browserless_options)
