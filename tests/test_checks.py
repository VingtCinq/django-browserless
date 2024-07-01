import pytest
from django.core.management import call_command


@pytest.fixture()
def browserless_settings(settings):
    # Browserless settings is a dict, intialize it if not defined
    settings.BROWSERLESS = getattr(settings, "BROWSERLESS", {})


def test_check_api_token_is_set(browserless_settings, settings, capsys):
    """If the Browserless API token is set then django check should issue a warning."""
    settings.BROWSERLESS = dict(settings.BROWSERLESS, API_TOKEN="")
    call_command("check")
    _, stderr = capsys.readouterr()
    assert "django_browserless.W001" in stderr, stderr


@pytest.mark.parametrize(
    "cache_import_string",
    [
        "django.core.cache.backends.locmem.LocMemCache",
        "django.core.cache.backends.dummy.DummyCache",
    ],
)
def test_check_cross_process_cache_is_set(cache_import_string, settings, capsys):
    """If a process-specific only cache is set then django check should issue a warning."""
    settings.CACHES["default"] = dict(
        settings.CACHES["default"], BACKEND=cache_import_string
    )
    call_command("check")
    _, stderr = capsys.readouterr()
    assert "django_browserless.W002" in stderr, stderr
