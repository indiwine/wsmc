import logging

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path

from social_media.tasks import perform_group_data_collection_task, perform_unknown_profiles_data_collection_task
from .helpers import generate_url_for_model, LinkTypes
from ..models import SuspectGroup

logger = logging.getLogger(__name__)


class SuspectGroupAdmin(ModelAdmin):

    def perform_scan(self, request: HttpRequest, object_id):
        perform_group_data_collection_task.delay(object_id)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, SuspectGroup, (object_id,)))

    def perform_unknown_profiles_scan(self, request: HttpRequest, object_id):
        perform_unknown_profiles_data_collection_task.delay(object_id)
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
