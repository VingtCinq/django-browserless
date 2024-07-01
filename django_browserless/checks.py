from django.core.checks import Tags, Warning, register


@register(Tags.compatibility)
def check_browserless_api_token_is_set(app_configs, **kwargs):
    from .settings import bl_settings

    errors = []
    if not bl_settings.API_TOKEN:
        errors.append(
            Warning(
                "Browserless API Token is not defined",
                hint="You must define an API_TOKEN entry in the BROWSERLESS settings dict",
                id="django_browserless.W001",
            )
        )
    return errors


@register(Tags.compatibility)
def check_cross_process_cache_is_set(app_configs, **kwargs):
    from django.conf import settings

    errors = []
    try:
        cache_backend_import_string = settings.CACHES["default"]["BACKEND"]
        if cache_backend_import_string in {
            "django.core.cache.backends.dummy.DummyCache",
            "django.core.cache.backends.locmem.LocMemCache",
        }:
            cache_backend = cache_backend_import_string.rsplit(".", maxsplit=1)[-1]
            errors.append(
                Warning(
                    f"The cache backend is set to {cache_backend} that isn't shared"
                    " among different processes and will prevent django-browserless"
                    " from working correctly.",
                    hint=(
                        "Please set a cross-process cache, see"
                        " https://docs.djangoproject.com/en/stable/topics/cache/#setting-up-the-cache"
                        " for more information."
                    ),
                    id="django_browserless.W002",
                ),
            )
    except KeyError:
        pass
    return errors
