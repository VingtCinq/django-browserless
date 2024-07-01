import pytest
from django_browserless import entities


class TestAuthenticationToken:
    def test_cannot_use_non_ascii_characters(self):
        """Authentication tokens will be eventually sent as HTTP headers, so they
        can only use ASCII characters."""
        with pytest.raises(ValueError):
            entities.AuthToken("é")
            entities.AuthToken("🚀")


class TestPDFRequest:
    def test_url_must_start_with_http_or_https(self):
        """PDFRequest URL must start with http or https (so that browserless can fetch
        it).
        """
        with pytest.raises(ValueError):
            entities.PDFRequest(url="example.com", user_id=1)
            entities.PDFRequest(url="ftp://example.com", user_id=1)
