from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.template.loader import render_to_string

from social_media.models import ScreeningDetail
from .helpers import LinkTypes, generate_link_for_model_object


class ScreeningDetailAdmin(ModelAdmin):
    actions = None
    list_display_links = None

    def formatted_content_object(self: ScreeningDetail):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.content_object, self.content_type.name)

    formatted_content_object.short_description = 'Сутність'

    def formatted_result(self: ScreeningDetail):
        return render_to_string(f'admin/social_media/screeningdetail/result_formatters/{self.module}.html', {
            'item': self
        })

    list_display = ['module', formatted_content_object, formatted_result]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False

    class Media:
        css = {
            'all': ('admin/css/screeningdetail/result-formatting.css',)
        }


admin.site.register(ScreeningDetail, ScreeningDetailAdmin)
