import json
import uuid
from typing import List

import asyncio
from celery.result import AsyncResult
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, StackedInline
from django.forms import Form, IntegerField, ImageField, ClearableFileInput
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe

from social_media.models import SuspectSocialMediaAccount, Suspect, SmProfile, OsintReport, OsintDetail
from social_media.tasks import perform_screening
from telegram_connection.admin_pages import CONFIRM_PAGE
from telegram_connection.exceptions import AccountNotLoggedIn
from telegram_connection.interaction.builder import BotBuilder
from telegram_connection.interaction.email_check.emailcheckrequest import EmailCheckRequest
from telegram_connection.interaction.name_check.namecheckrequest import NameCheckRequest
from telegram_connection.interaction.phone_check.phonecheckrequest import PhoneCheckRequest
from telegram_connection.interaction.sm_check.smcheckrequest import SmCheckRequest
from .helpers import LinkTypes
from .helpers import generate_url_for_model, generate_url_for_model_object
from ..ai.loader import get_model
from ..ai.models.vatadetectormodel import VataPredictionItem
from ..osint.holehe_connector.holeheagent import HoleheAgent
from ..osint.osintmodules import OsintModules
from ..webdriver.management import collect_and_process


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


class VataDetectorDemoForm(Form):
    probability = IntegerField(label='Поріг впевненості (%)', min_value=1, max_value=99, initial=50)
    iou = IntegerField(label='IoU', min_value=1, max_value=99, initial=50)
    images = ImageField(label='Зображення', widget=ClearableFileInput(attrs={'multiple': True}))


class SuspectAdmin(ModelAdmin):
    inlines = [LinkedSmAccounts, LinkedSmProfile]
    search_fields = ['name']
    readonly_fields = ['score']
    list_display = ['__str__', 'score']

    def perform_scan(self, request: HttpRequest, object_id):
        with_posts = True
        if 'profile_only' in request.GET:
            with_posts = False

        asyncio.run(collect_and_process(object_id, with_posts), debug=settings.DEBUG)

        # perform_sm_data_collection(object_id, with_posts)
        # result: AsyncResult = perform_sm_data_collection.delay(object_id, with_posts)
        # self._send_message(request, result)
        # return redirect(generate_url_for_model(LinkTypes.CHANGE, Suspect, (object_id,)))

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

    def detector_demo(self, request: HttpRequest):
        check_results = None
        model = get_model()
        if request.method == 'POST':
            form = VataDetectorDemoForm(request.POST, request.FILES)
            if form.is_valid():
                pr = form.cleaned_data['probability'] / 100
                iou = form.cleaned_data['iou'] / 100
                img_paths = []
                check_results = []
                for uploaded_file in form.files.getlist('images'):
                    img_path = uploaded_file.temporary_file_path()

                    img_paths.append(img_path)
                    check_results.append({
                        'img': img_path,
                        'boxes': None
                    })
                predictions = model.predict(img_paths, pr, iou)
                for i, prediction in enumerate(predictions):
                    check_results[i]['boxes'] = json.dumps(self._convert_prediction_to_w3c(prediction))

        else:
            form = VataDetectorDemoForm()
        context = {
            "title": mark_safe("Ватний детектор &beta;"),
            "form_url": request.get_full_path(),
            "form": form,
            "check_results": check_results,
            "model_name": model.name,
            **self.admin_site.each_context(request),
        }

        return TemplateResponse(
            request, 'admin/social_media/suspect/detector_demo.html', context)

    @staticmethod
    def _convert_prediction_to_w3c(prediction: List[VataPredictionItem]) -> List[dict]:
        result = []
        for item in prediction:
            result.append({
                "@context": "http://www.w3.org/ns/anno.jsonld",
                "id": f"#{uuid.uuid4()}",
                "type": "Annotation",
                "body": [{
                    "type": "TextualBody",
                    "value": f'{item.label}: {round(item.pr * 100)}%',
                    "label": item.label
                }],
                "target": {
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                        "value": f"xywh=pixel:{item.x},{item.y},{item.width},{item.height}"
                    }
                }
            })

        return result

    def _send_message(self, request: HttpRequest, result: AsyncResult):
        self.message_user(request,
                          mark_safe(f'Задача "{result.task_id}" поставлена в чергу зі сатусом "{result.state}"'),
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
                 name='%s_%s_perform_osint' % (opts.app_label, opts.model_name)),
            path('detector-demo', self.detector_demo,
                 name='%s_%s_detector_demo' % (opts.app_label, opts.model_name))
        ]
        return ursl + additional_urls


admin.site.register(Suspect, SuspectAdmin)
