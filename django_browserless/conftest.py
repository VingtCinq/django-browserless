import pytest
from django.test import override_settings

TEST_SETTINGS = {
    "DEBUG": False,
    "CACHES": {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    "BROWSERLESS": {"API_TOKEN": "foobar"},
}


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    with override_settings(**TEST_SETTINGS):
        yield
