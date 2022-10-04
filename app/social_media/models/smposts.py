from django.db.models import Model, ForeignKey, CASCADE, TextField, DateTimeField
from .smprofile import SmProfile

class SmPosts(Model):
    profile = ForeignKey(SmProfile, on_delete=CASCADE)
    datetime = DateTimeField(null=True)
    body = TextField()