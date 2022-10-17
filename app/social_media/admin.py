from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import SmCredential

admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'


class SmCredentialsAdmin(ModelAdmin):
    list_display = ('user_name', 'social_media')


admin.site.register(SmCredential, SmCredentialsAdmin)
