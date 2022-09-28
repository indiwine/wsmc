from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import SmCredentials


class SmCredentialsAdmin(ModelAdmin):
    list_display = ('user_name', 'social_media')
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super().get_readonly_fields(request, obj)
        return ['social_media']



admin.site.register(SmCredentials, SmCredentialsAdmin)
