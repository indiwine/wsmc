from django.db.models import Model, ForeignKey, CASCADE, CharField, JSONField

from .osintreport import OsintReport
from ..osint.osintmodules import OsintModules


class OsintDetail(Model):
    report = ForeignKey(OsintReport, on_delete=CASCADE)
    module = CharField(max_length=50, choices=OsintModules.choices)
    sub_module = CharField(max_length=128, null=True, default=None)
    result = JSONField()

