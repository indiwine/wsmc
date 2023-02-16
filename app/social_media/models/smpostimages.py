from django.db.models import Model, ForeignKey, CASCADE, URLField, CharField, Index, ImageField

from .smpost import SmPost


class SmPostImages(Model):
    post = ForeignKey(SmPost, on_delete=CASCADE, editable=False)
    oid = CharField()
    url = URLField(null=True, editable=False)
    image = ImageField(upload_to='post_images')

    class Meta:
        indexes = [
            Index(fields=['post', 'oid'])
        ]
