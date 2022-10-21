from celery.result import AsyncResult
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, StackedInline
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path
from django_celery_results.models import TaskResult
from django.utils.safestring import mark_safe

from social_media.models import SuspectSocialMediaAccount, Suspect, SmProfile
# from social_media.screening.screener import Screener
# from social_media.social_media import SocialMediaEntities
# from social_media.webdriver import Request, Agent
from social_media.tasks import perform_sm_data_collection, perform_screening
from .helpers import generate_url_for_model
from .helpers import LinkTypes, generate_link_for_model_object


class LinkedSmProfile(StackedInline):
    model = SmProfile

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LinkedSmAccounts(StackedInline):
    model = SuspectSocialMediaAccount
    extra = 1


class SuspectAdmin(ModelAdmin):
    inlines = [LinkedSmAccounts, LinkedSmProfile]
    search_fields = ['name']
    readonly_fields = ['score']
    list_display = ['name', 'score']

    def perform_scan(self, request: HttpRequest, object_id):
        result: AsyncResult = perform_sm_data_collection(object_id)
        self._send_message(request, result)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, Suspect, (object_id,)))

    def perform_screening(self, request: HttpRequest, object_id):
        result: AsyncResult = perform_screening.delay(object_id)
        self._send_message(request, result)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, Suspect, (object_id,)))

    def _send_message(self, request: HttpRequest, result: AsyncResult):
        # tk = TaskResult.objects.get_task(result.task_id)
        # link = generate_link_for_model_object(LinkTypes.CHANGE, tk, result.task_id)

        self.message_user(request, mark_safe(f'Задача "{result.task_id}" поставлена в чергу зі сатусом "{result.state}"'),
                          messages.SUCCESS)

    def get_urls(self):
        ursl = super().get_urls()
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/perform-scan', self.perform_scan,
                 name='%s_%s_perform_scan' % (opts.app_label, opts.model_name)),
            path('<path:object_id>/perform-screening', self.perform_screening,
                 name='%s_%s_perform_screening' % (opts.app_label, opts.model_name))
        ]
        return ursl + additional_urls


admin.site.register(Suspect, SuspectAdmin)
