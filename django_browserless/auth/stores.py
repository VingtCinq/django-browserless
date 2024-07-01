import logging
from typing import Protocol

from django.core.cache import cache

from .. import entities
from ..settings import bl_settings

_logger = logging.getLogger(__name__)


class AuthenticationStore(Protocol):
    """Interface that a authentication store must implement:
    - a set() method to store the auth token and the pdf request details
    - a get() method to retrieve the pdf request details from the auth token

    Its purpose is to store a secret associated with a user's identity that can be
    retrieve later on when receiving Browserless requests to authenticate them as the
    user who requested the PDF generation.
    """

    def set(
        self,
        auth_token: entities.AuthToken,
        pdf_request: entities.PDFRequest,
        timeout: int = None,
    ): ...

    def get(self, auth_token: str) -> entities.PDFRequest | None: ...


class CacheStore:
    """AuthenticationStore implementation that relies on Django's cache."""

    def __init__(self) -> None:
        self._cache = cache

    def set(
        self,
        auth_token: entities.AuthToken,
        pdf_request: entities.PDFRequest,
        timeout: int = None,
    ):
        if timeout is None:
            timeout = bl_settings.DEFAULT_AUTH_TIMEOUT
        self._cache.set(auth_token, pdf_request, timeout=timeout)
        _logger.debug("Set cache for %s", auth_token)

    def get(self, auth_token: str) -> entities.PDFRequest | None:
        value = self._cache.get(auth_token)
        if value is None:
            _logger.debug("Cache miss for %s", auth_token)
        else:
            _logger.debug("Cache hit for %s", auth_token)
        return value
