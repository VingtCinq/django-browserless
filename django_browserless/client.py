from __future__ import annotations

import copy
import logging
from urllib.parse import urlencode

import httpx

from .entities import AuthToken
from .settings import bl_settings

_logger = logging.getLogger(__name__)


class BrowserlessClientError(Exception):
    pass


def fetch_pdf(
    url: str, options: dict | None = None, auth_token: AuthToken | None = None
) -> bytes:
    """Returns the PDF content from the URL, as bytes."""
    if options is not None:
        options = _merge_options(bl_settings.DEFAULT_PDF_OPTIONS, options)
    else:
        options = bl_settings.DEFAULT_PDF_OPTIONS
    if auth_token is not None:
        extra_http_headers = options.setdefault("setExtraHTTPHeaders", {})
        extra_http_headers[bl_settings.AUTH_HEADER_NAME] = auth_token
    try:
        response = httpx.post(
            url=(
                bl_settings.PDF_URL + "?" + urlencode({"token": bl_settings.API_TOKEN})
            ),
            json={"url": url, **options},
            timeout=bl_settings.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.content
    except httpx.HTTPError as exc:
        _logger.debug("Browserless error: %s", str(exc))
        if locals().get("response") is not None:
            _logger.debug("Request body was %s", response.request.content.decode())
            _logger.debug("Response body was %s", response.content.decode())
        raise BrowserlessClientError(str(exc)) from exc


def _merge_options(dict1: dict, dict2: dict) -> dict:
    """Deeply merge two dictionaries, including nested dictionaries (dict 2 values win)
    and lists (list 2 values replace list 1 values or append to it).
    """
    out = copy.deepcopy(dict1)  # don't mutate dict1
    for key in dict2:
        if key in out:
            if isinstance(out[key], dict) and isinstance(dict2[key], dict):
                out[key] = _merge_options(out[key], dict2[key])
            elif isinstance(out[key], list) and isinstance(dict2[key], list):
                out[key] = out[key] + [val for val in dict2[key] if val not in out[key]]
            else:
                out[key] = dict2[key]
        else:
            out[key] = dict2[key]
    return out
