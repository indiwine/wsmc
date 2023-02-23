from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import SmPostImage


class SmPostImageAdmin(ModelAdmin):
    actions = None
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False

    class Media:
        css = {
            'all': ('admin/css/suspect/annotorious.min.css',)
        }
        js = ('admin/js/annotorious.min.js', 'admin/js/annotations.js')


admin.site.register(SmPostImage, SmPostImageAdmin)
