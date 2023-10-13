from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet

from social_media.models import SuspectPlace
from social_media.tasks import discover_profiles


@admin.action(description="Discover profiles")
def perform_discovery(modeladmin, request, queryset: QuerySet[SuspectPlace]):
    for place in queryset:
        discover_profiles.delay(place.id)

class SuspectPlaceAdmin(ModelAdmin):
    readonly_fields = ['place_collected']
    actions = [perform_discovery]

admin.site.register(SuspectPlace, SuspectPlaceAdmin)
