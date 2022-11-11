from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..models.telegrambot import TelegramBot


class TelegramBotAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TelegramBot, TelegramBotAdmin)
