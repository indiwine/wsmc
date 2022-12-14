from celery.result import AsyncResult
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, StackedInline
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path
from django.utils.safestring import mark_safe

from social_media.models import SuspectSocialMediaAccount, Suspect, SmProfile, OsintReport, OsintDetail
from social_media.tasks import perform_sm_data_collection, perform_screening
from telegram_connection.admin_pages import CONFIRM_PAGE
from telegram_connection.exceptions import AccountNotLoggedIn
from telegram_connection.interaction.builder import BotBuilder
from telegram_connection.interaction.email_check.emailcheckrequest import EmailCheckRequest
from telegram_connection.interaction.name_check.namecheckrequest import NameCheckRequest
from telegram_connection.interaction.phone_check.phonecheckrequest import PhoneCheckRequest
from telegram_connection.interaction.sm_check.smcheckrequest import SmCheckRequest
from .helpers import LinkTypes
from .helpers import generate_url_for_model, generate_url_for_model_object
from ..osint.holehe_connector.holeheagent import HoleheAgent
from ..osint.osintmodules import OsintModules


class LinkedSmProfile(StackedInline):
    model = SmProfile
    readonly_fields = ['id_url']

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
    list_display = ['__str__', 'score']

    def perform_scan(self, request: HttpRequest, object_id):
        with_posts = True
        if 'profile_only' in request.GET:
            with_posts = False

        result: AsyncResult = perform_sm_data_collection.delay(object_id, with_posts)
        self._send_message(request, result)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, Suspect, (object_id,)))

    def perform_screening(self, request: HttpRequest, object_id):
        result: AsyncResult = perform_screening.delay(object_id)
        self._send_message(request, result)
        return redirect(generate_url_for_model(LinkTypes.CHANGE, Suspect, (object_id,)))

    def perform_osint(self, request: HttpRequest, object_id):
        # TODO: Refactor method. Move logic somewhere.
        suspect: Suspect = Suspect.objects.get(id=object_id)
        check_requests = []

        if suspect.has_name:
            check_requests.append(NameCheckRequest().set_arguments(suspect.name))

        if suspect.email:
            check_requests.append(EmailCheckRequest().set_arguments(suspect.email))

        if suspect.phone:
            check_requests.append(PhoneCheckRequest().set_arguments(str(suspect.phone), suspect.__str__()))

        suspect_sm_accounts = SuspectSocialMediaAccount.objects.filter(suspect=suspect)
        if len(suspect_sm_accounts) > 0:
            sm_check_request = SmCheckRequest()
            for sm_account in suspect_sm_accounts:
                sm_check_request.add_sm(sm_account.fetch_bot_check_link(), sm_account.credentials.social_media)
            check_requests.append(sm_check_request)

        try:
            check_result = BotBuilder.process_requests(check_requests)
        except AccountNotLoggedIn as e:
            return redirect(
                generate_url_for_model_object(CONFIRM_PAGE, e.tg_account, params={'back_to': request.get_full_path()})
            )

        report = OsintReport(suspect=suspect)
        report.save()
        for ic, result in check_result:
            OsintDetail(
                report=report,
                module=OsintModules.from_interation_request(ic.request),
                sub_module=ic.bot.get_name(),
                result={"text": result}
            ).save()

        if suspect.email:
            out = HoleheAgent.check_email(suspect.email)
            for check in out:
                OsintDetail(
                    report=report,
                    module=OsintModules.HOLEHE_EMAIL,
                    sub_module=check['domain'],
                    result=check).save()

        return redirect(generate_url_for_model(LinkTypes.CHANGELIST, OsintDetail, params={"report_id": report.id}))

    def _send_message(self, request: HttpRequest, result: AsyncResult):
        self.message_user(request,
                          mark_safe(f'???????????? "{result.task_id}" ???????????????????? ?? ?????????? ???? ?????????????? "{result.state}"'),
                          messages.SUCCESS)

    def get_urls(self):
        ursl = super().get_urls()
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/perform-scan', self.perform_scan,
                 name='%s_%s_perform_scan' % (opts.app_label, opts.model_name)),
            path('<path:object_id>/perform-screening', self.perform_screening,
                 name='%s_%s_perform_screening' % (opts.app_label, opts.model_name)),
            path('<path:object_id>/perform-osint', self.perform_osint,
                 name='%s_%s_perform_osint' % (opts.app_label, opts.model_name))
        ]
        return ursl + additional_urls


admin.site.register(Suspect, SuspectAdmin)
