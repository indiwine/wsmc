from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..models import TelegramAccount


class TelegramAccountAdmin(ModelAdmin):
    readonly_fields = ['name', 'logged_in']
    save_as_continue = False


    def get_input_tg_file(self, request):
        pass

    def get_urls(self):
        additional_urls = [

        ]

        return additional_urls + super().get_urls()

    # def response_add(self, request, obj, post_url_continue=None):


admin.site.register(TelegramAccount, TelegramAccountAdmin)
