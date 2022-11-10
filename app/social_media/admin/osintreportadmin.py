from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.models import OsintDetail, OsintReport
from .helpers import generate_link_for_model, LinkTypes, generate_link_for_model_object


class OsintReportAdmin(ModelAdmin):
    list_display_links = None
    list_filter = ['suspect', 'created_at']

    def details_link(self):
        return generate_link_for_model(LinkTypes.CHANGELIST, OsintDetail, "Деталі", params={"report_id": self.id})

    def suspect_link(self):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.suspect, self.suspect.__str__())

    list_display = ['__str__', suspect_link, details_link, 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(OsintReport, OsintReportAdmin)
