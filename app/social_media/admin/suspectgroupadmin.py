import logging

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path

from social_media.tasks import perform_group_data_collection_task, perform_ok_group_data_collection_task
from .helpers import generate_url_for_model, LinkTypes
from ..models import SuspectGroup
from ..social_media import SocialMediaTypes

logger = logging.getLogger(__name__)


def distribute_task_to_groups(group: SuspectGroup):
    if group.social_media_type == SocialMediaTypes.OK:
        perform_ok_group_data_collection_task.delay(group.id)
        return
    perform_group_data_collection_task.delay(group.id)


@admin.action(description="Collect")
def perform_collect(modeladmin, request, queryset: QuerySet[SuspectGroup]):
    for group in queryset:
        distribute_task_to_groups(group)


class SuspectGroupAdmin(ModelAdmin):
    list_display = ['url', 'id']
    ordering = ['-id']
    actions = [perform_collect]

    def perform_scan(self, request: HttpRequest, object_id):
        perform_group_data_collection_task.delay(object_id)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, SuspectGroup, (object_id,)))

    def perform_unknown_profiles_scan(self, request: HttpRequest, object_id):
        group: SuspectGroup = self.get_object(request, object_id)
        distribute_task_to_groups(group)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, SuspectGroup, (object_id,)))

    def get_urls(self):
        ursl = super().get_urls()
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/perform-scan', self.perform_scan,
                 name='%s_%s_perform_scan' % (opts.app_label, opts.model_name)),
            path('<path:object_id>/perform-unknown-scan', self.perform_unknown_profiles_scan,
                 name='%s_%s_perform_unknown_scan' % (opts.app_label, opts.model_name)),
        ]
        return ursl + additional_urls


admin.site.register(SuspectGroup, SuspectGroupAdmin)
