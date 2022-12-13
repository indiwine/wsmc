from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import ScreeningReport, ScreeningDetail
from .helpers import generate_link_for_model, LinkTypes, generate_link_for_model_object


class ScreeningReportAdmin(ModelAdmin):
    list_display_links = None
    ordering = ['-created_at']

    def details_link(self):
        return generate_link_for_model(LinkTypes.CHANGELIST, ScreeningDetail, "Деталі", params={"report_id": self.id})

    details_link.short_description = 'Деталі'

    def suspect_link(self):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.suspect, self.suspect.__str__())

    suspect_link.short_description = 'Людина'

    list_display = ['name', 'resulting_score', suspect_link, 'created_at', details_link]
    list_filter = ['suspect', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ScreeningReport, ScreeningReportAdmin)
