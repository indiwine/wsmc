from django.db.models import Model, DateTimeField, CharField, PositiveIntegerField, ForeignKey, CASCADE

from social_media.models.suspect import Suspect


class ScreeningReport(Model):
    name = CharField(editable=False, max_length=255)
    resulting_score = PositiveIntegerField(default=0)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
