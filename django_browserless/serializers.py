from rest_framework import serializers


class UrlToPdf(serializers.Serializer):
    url = serializers.URLField()
    filename = serializers.CharField(max_length=255)
    content_disposition = serializers.ChoiceField(
        choices=[("inline", "Inline"), ("attachment", "Attachment")],
        required=False,
    )
    browserless_options = serializers.JSONField(required=False)
