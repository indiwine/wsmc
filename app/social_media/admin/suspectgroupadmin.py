from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..models import SuspectGroup


class SuspectGroupAdmin(ModelAdmin):
    pass


admin.site.register(SuspectGroup, SuspectGroupAdmin)
