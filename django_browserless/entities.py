from attrs import field, frozen


class AuthToken(str):
    def __init__(self, string):
        super().__init__()
        # The authentication token will be passed as a cookie, i.e. sent as a HTTP
        # header and it's safer to use only ASCII characters
        if not self.isascii():
            raise ValueError("Token must be ASCII")


def _url_must_start_with_http_or_https(instance, attribute, value):
    if not value.startswith("http://") and not value.startswith("https://"):
        raise ValueError("URL must start with 'http://' or 'https://'")


@frozen
class PDFRequest:
    url: str = field(validator=_url_must_start_with_http_or_https)
    user_id: int | None = None
