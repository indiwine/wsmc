from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline

from social_media.models import SuspectSocialMediaAccount, Suspect


class LinkedSmAccounts(StackedInline):
    model = SuspectSocialMediaAccount
    extra = 1

class SuspectAdmin(ModelAdmin):
    inlines = [LinkedSmAccounts]
    search_fields = ['name']

admin.site.register(Suspect, SuspectAdmin)