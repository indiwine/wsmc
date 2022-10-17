from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import BlackPhrase


class BlackPhraseAdmin(ModelAdmin):
    list_display = ('phrase',)


admin.site.register(BlackPhrase, BlackPhraseAdmin)
