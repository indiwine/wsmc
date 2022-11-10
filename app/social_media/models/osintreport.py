from django.db.models import Model, ForeignKey, CASCADE, DateTimeField

from .suspect import Suspect


class OsintReport(Model):
    suspect = ForeignKey(Suspect, on_delete=CASCADE, editable=False)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'OSINT по {self.suspect.name}'

    class Meta:
        verbose_name = 'OSINT'
        verbose_name_plural = 'OSINT'
