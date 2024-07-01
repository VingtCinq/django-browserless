from django.conf import settings as django_settings
from django.core.signals import setting_changed

DEFAULTS = {
    "API_TOKEN": "",
    "AUTH_HEADER_NAME": "x-bl-auth",
    "AUTH_STORE": "django_browserless.auth.stores.CacheStore",
    "DEFAULT_AUTH_TIMEOUT": 30,  # seconds
    "DEFAULT_PDF_OPTIONS": {
        "options": {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "format": "A4",
        },
        "gotoOptions": {"waitUntil": "networkidle0"},
    },
    "DEFAULT_TIMEOUT": 30,  # seconds
    "PDF_URL": "https://chrome.browserless.io/pdf",
}
BROWSERLESS_SETTINGS_KEY = "BROWSERLESS"


class BrowserlessSettings:
    def __init__(self, defaults):
        self._defaults = defaults
        self.load()

    def load(self):
        self._settings = {
            **self._defaults,
            **getattr(django_settings, BROWSERLESS_SETTINGS_KEY, {}),
        }

    def __getattr__(self, attr):
        if attr.startswith("_"):
            return getattr(self, attr)
        return self._settings[attr]


bl_settings = BrowserlessSettings(defaults=DEFAULTS)


def reload_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == BROWSERLESS_SETTINGS_KEY:
        bl_settings.load()


setting_changed.connect(reload_settings)
