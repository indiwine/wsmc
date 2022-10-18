from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.template.loader import render_to_string

from social_media.models import ScreeningReport, ScreeningDetail
from .helpers import generate_link_for_model, LinkTypes, generate_link_for_model_object


class ScreeningReportAdmin(ModelAdmin):
    list_display_links = None

    def details_link(self):
        return generate_link_for_model(LinkTypes.CHANGELIST, ScreeningDetail, "Деталі", params={"report_id": self.id})

    def suspect_link(self):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.suspect, self.suspect.__str__())

    list_display = ['name', 'resulting_score', suspect_link, 'created_at', details_link]
    list_filter = ['suspect', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ScreeningDetailAdmin(ModelAdmin):
    actions = None
    list_display_links = None

    def formatted_content_object(self):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.content_object, self.content_type.name)

    formatted_content_object.short_description = 'Сутність'

    def formatted_result(self):
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


admin.site.register(ScreeningReport, ScreeningReportAdmin)
admin.site.register(ScreeningDetail, ScreeningDetailAdmin)
