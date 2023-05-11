from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import SmProfileLocationFilter


class SmProfileLocationFilterAdmin(ModelAdmin):
    ordering = ['-id']
    filter_horizontal = ['locations']

admin.site.register(SmProfileLocationFilter, SmProfileLocationFilterAdmin)
