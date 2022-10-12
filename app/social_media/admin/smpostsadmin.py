from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import SmPosts


class SmPostsAdmin(ModelAdmin):
    list_display = ('profile', 'social_media', 'datetime', 'permalink', 'body')
    list_filter = ('profile', 'social_media', 'datetime')
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(SmPosts, SmPostsAdmin)