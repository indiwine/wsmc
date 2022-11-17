from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.template.loader import render_to_string

from social_media.models import OsintDetail


class OsintDetailAdmin(ModelAdmin):
    actions = None
    list_display_links = None

    def formatted_result(self: OsintDetail):
        return render_to_string(f'admin/social_media/osintdetail/result_formatters/{self.module}.html', {
            'item': self
        })

    list_display = ['module', 'sub_module', formatted_result]
    list_filter = ['module']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False

    class Media:
        css = {
            'all': ('admin/css/osintdetail/result-formatting.css',)
        }


admin.site.register(OsintDetail, OsintDetailAdmin)
