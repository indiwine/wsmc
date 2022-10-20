from django.contrib.admin import ModelAdmin
from django.contrib import admin

from social_media.models import SmProfile


class SmProfileAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False


admin.site.register(SmProfile, SmProfileAdmin)
