from django import forms


class UrlToPdf(forms.Form):
    # url = forms.URLField(assume_scheme="https")
    url = forms.URLField()
    filename = forms.CharField(max_length=255)
    content_disposition = forms.ChoiceField(
        choices=[("inline", "Inline"), ("attachment", "Attachment")],
        required=False,
    )
    browserless_options = forms.JSONField(required=False)
