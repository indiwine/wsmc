from django.db.models import Model, URLField, CharField


class SuspectGroup(Model):
    name = CharField(max_length=255, null=True, blank=True)
    url = URLField()

    def __str__(self):
        if not self.name:
            return f'Untitled group {self.id}'

        return self.name

