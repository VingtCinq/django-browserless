# Django Browserless

Django Browserless is a package that offers Django and Django REST framework views for generating PDFs from any URL using [browserless](https://www.browserless.io/).

## Table of Contents
- [Django Browserless](#django-browserless)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Getting started](#getting-started)
  - [Generating PDFs from views requiring authentication](#generating-pdfs-from-views-requiring-authentication)
  - [Using from Python code](#using-from-python-code)
  - [Specifying browserless options](#specifying-browserless-options)
  - [Additional configuration options](#additional-configuration-options)
    - [Authentication timeout](#authentication-timeout)
    - [Default browserless timeout](#default-browserless-timeout)
    - [Default PDF generation options](#default-pdf-generation-options)
  - [How it works](#how-it-works)

## Features
- Generate a PDF from any URL
- Support for both Django and Django REST framework views
- Custom authentication mechanism for secure PDF generation
- Configurable browserless options

## Requirements

 - Python 3.8+
  - Django 4.2+
  - Django REST framework 3.12+

## Getting started

Install using pip
```
python -m pip install django-browserless
```

Add django_browserless to your INSTALLED_APPS in your Django settings:
```python
INSTALLED_APPS = [
    ...
    "django_browserless",
]
```

Add `BROWSERLESS` to your settings and fill in your browserless API token:
```python
BROWSERLESS = {
    "API_TOKEN": "your-api-token",
}
```

Add PDF generation view to your `urls.py`, either using a Django view:
```python
from django_browserless.views.django_views import url_to_pdf
...
urlpatterns = [
   ...
    path("pdf/", url_to_pdf),
]
```

You can now generate a PDF from any URL, e.g.:
```
curl -XPOST -d 'url=http://example.com filename=example.pdf' 'http://localhost/pdf/'
```

Or a Django REST framework view:
```python
from django_browserless.views.drf_views import UrlToPdf
...
urlpatterns = [
   ...
    path("pdf/", UrlToPdf.as_view()),
]
````

You can now generate a PDF from any URL, e.g.:
```
curl -XPOST -H "Content-type: application/json" -d 'url=http://example.com filename=example.pdf' 'http://localhost/pdf/'
```

## Generating PDFs from views requiring authentication

If PDF generation needs to access any authenticated views in your project, you must configure browserless to authenticate these calls.

For Django views you must use the `browserless_authenticated` decorator, e.g.:
```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django_browserless.auth.authenticators import browserless_authenticated


@browserless_authenticated
@login_required
def authenticated_view(request):
    return HttpResponse(f"Hello {request.user.username}!")

```

For Django REST framework views you must use the `BrowserlessAuthentication` authentication class, e.g. (assuming you're using DRF token authentication):
```python
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class AuthenticatedAPIView(APIView):
    authentication_classes = [TokenAuthentication, BrowserlessAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return HttpResponse(f"Hello {request.user.username}!")
```

## Using from Python code

Apart from the views that can be called from the frontend `django-browserless` can also be used directly from Python code on the backend.
```python
from django_browserless import pdf

pdf_content = pdf.from_url(url="http://example.com")

# A user can be specified if browserless need to call views that require authentication:
pdf_content = pdf.from_url(url="https://project.tld/export/", as_user_id=1)

# Browserless options can also be passed as a dictionary:
pdf_content = pdf.from_url(
    url="https://example.com", browserless_options={"landscape": True}
)
```

## Specifying browserless options

You can specify any option supported by browserless for PDF generation (through its request body `option` field). They will be merged with the default options (see [Default browserless timeout](#default-browserless-timeout)) using the `browserless_options` field in your request body, e.g.:
```json
{
    "url": "http://example.com",
    "filename": "example.pdf",
    "browserless_options": {
        "landscape": true,
        "displayHeaderFooter": true
    }
}
```

## Additional configuration options

### Authentication timeout

In case browserless call views from your project that require authentication, this is the lifetime of the authentication credentials used by browserless (30 seconds by default, see [How it works](#how-it-works) for more details):
```python
BROWSERLESS = {
    "DEFAULT_AUTH_TIMEOUT": 30,  # seconds
}
```

### Default browserless timeout

Timeout for generating a PDF (30 seconds by default):
```python
BROWSERLESS = {
    "DEFAULT_AUTH_TIMEOUT": 30,  # seconds
}
```

### Default PDF generation options

Default browserless PDF generation options, see [browserless documentation](https://docs.browserless.io/open-api/#tag/Browser-REST-APIs/paths/~1chrome~1pdf/post):
```python
BROWSERLESS = {
    "DEFAULT_PDF_OPTIONS": {
        "options": {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "format": "A4",
        },
        "gotoOptions": {"waitUntil": "networkidle0"},
    },
}
```

## How it works

At its core, `django-browserless` consists in two parts:
 - A thin wrapper around the [browserless PDF HTTP API](https://docs.browserless.io/HTTP-APIs/pdf).
 - A custom authentication mechanism that allow browserless to impersonate the user's who requested the PDF generation.

Indeed, more often than not, the page to turn into a PDF contains user-specific content and requires authentication. However, as browserless is a 3rd-party service, it is not authenticated as the user who requested the PDF generation.

`django-browserless` addresses this issue using a custom, time-limited authentication mechanism. Here is how it is implemented:
- Whenever a page is requested to be turned into a PDF, a random secret is generated, associated with request's user and page, and stored for a short period of time. In a typical production setup with multiple Python processes that don't share memory, the required data must be accessible to all processes. This leaves the database and the global cache as the most straightforward options. The global cache is faster and has a built-in expiration time mechanism so it's used rather than the database.
- The random secret is shared with Browserless [as an extra HTTP header that will be added to all requests](https://docs.browserless.io/open-api/#tag/Browser-REST-APIs/paths/~1chrome~1pdf/post) that browserless will automatically send with all the requests to this page.
- The views called by browserless extract the random secret from the request and check it against the ones stored in the global cache. If there is a match, the user associated with the secret is attached to the request.