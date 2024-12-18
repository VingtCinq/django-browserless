from unittest.mock import Mock

import django
import pytest


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django_browserless",
            "rest_framework",
        ),
        ROOT_URLCONF="tests.urls",
    )
    django.setup()


@pytest.fixture
def patch_pdf_fetching(monkeypatch):
    monkeypatch.setattr(
        "django_browserless.pdf.client.fetch_pdf", lambda **_: b"content"
    )


@pytest.fixture
def fail_pdf_fetching(monkeypatch):
    from django_browserless.client import BrowserlessClientError

    monkeypatch.setattr(
        "django_browserless.pdf.client.fetch_pdf",
        Mock(side_effect=BrowserlessClientError("Something wrong happened")),
    )
