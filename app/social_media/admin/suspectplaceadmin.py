from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import SuspectPlace


class SuspectPlaceAdmin(ModelAdmin):
    readonly_fields = ['place_collected']

admin.site.register(SuspectPlace, SuspectPlaceAdmin)
