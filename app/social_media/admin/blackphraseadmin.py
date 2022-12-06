from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import BlackPhrase


class BlackPhraseAdmin(ModelAdmin):
    list_display = ('phrase',)
    search_fields = ('phrase',)
    ordering = ['phrase']

    class Media:
        css = {
            'all': ('admin/css/blackphrase/phrase-tag.css',)
        }


admin.site.register(BlackPhrase, BlackPhraseAdmin)
