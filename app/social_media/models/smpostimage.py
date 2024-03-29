from django.db.models import Model, ForeignKey, CASCADE, URLField, CharField, Index, ImageField, JSONField

from .smpost import SmPost


class SmPostImage(Model):
    post = ForeignKey(SmPost, on_delete=CASCADE)
    oid = CharField(max_length=2512, editable=False)
    url = URLField(null=True, editable=False)
    permalink = URLField(null=True)
    image = ImageField(upload_to='post_images', null=True, default=None)
    prediction = JSONField(null=True, default=None, editable=False)

    class Meta:
        indexes = [
            Index(fields=['post', 'oid', 'prediction'])
        ]
