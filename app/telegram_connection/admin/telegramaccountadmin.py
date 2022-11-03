import logging

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.forms import Form, CharField
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from telegram.client import AuthorizationState

from social_media.admin.helpers import generate_url_for_model_object, LinkTypes
from ..connection import build_client
from ..models import TelegramAccount

logger = logging.getLogger(__name__)


class OtpForm(Form):
    password = CharField()


class TelegramAccountAdmin(ModelAdmin):
    list_display = ['phone', 'name', 'logged_in']
    readonly_fields = ['name', 'logged_in']
    save_as_continue = False

    def has_change_permission(self, request, obj=None):
        return False

    def confirm_tg_login(self, request: HttpRequest, object_id):
        account: TelegramAccount = self.get_object(request, object_id)
        tg = build_client(account.phone.__str__())
        code = tg.login(False)
        logger.info(f'TG status: {code}')
        try:

            if code == AuthorizationState.READY:
                self.message_user(request, 'Логін успішний', messages.SUCCESS)
                return redirect(request.GET['back_to'])

            if code == AuthorizationState.WAIT_REGISTRATION:
                self.message_user(request, 'Телефон не зареєстровано в телеграмі', messages.ERROR)
                return redirect(request.GET['back_to'])

            form = None

            if request.method == 'POST':
                form = OtpForm(request.POST)
                if form.is_valid():
                    otp_or_pass = form.cleaned_data['password']

                    if code == AuthorizationState.WAIT_CODE:
                        tg.send_code(otp_or_pass)
                    elif code == AuthorizationState.WAIT_PASSWORD:
                        tg.send_password(otp_or_pass)
                    else:
                        self.message_user(request, f'Unknown code "{code}" received during login to telegram',
                                          messages.ERROR)
                    me = tg.get_me()
                    me.wait()
                    account.name = self._extract_user_name(me)
                    account.logged_in = True
                    account.save()
                    return redirect(request.GET['back_to'])

            if code == AuthorizationState.WAIT_CODE or code == AuthorizationState.WAIT_PASSWORD:
                form = OtpForm()
                input_text = 'Введіть одноразовий пароль який телеграм відправив вам на телефон:'
                if code == AuthorizationState.WAIT_PASSWORD:
                    input_text = 'Введіть свій пароль:'

            context = {
                "title": "Login Into Telegram",
                "form_url": request.get_full_path(),
                "form": form,
                "account": account,
                "input_text": input_text,
                **self.admin_site.each_context(request),
            }

            return TemplateResponse(
                request, 'admin/telegram_connection/telegramaccount/confirm.html', context)
        finally:
            tg.stop()

    def get_urls(self):
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/confirm', self.confirm_tg_login,
                 name='%s_%s_confirm' % (opts.app_label, opts.model_name)),
        ]

        return additional_urls + super().get_urls()

    def _extract_user_name(self, me) -> str:
        username: str = me.update['first_name']
        username = username.strip()
        username += me.update['last_name']
        username = username.strip()
        nickname: str = me.update['username']
        if len(nickname) > 0:
            username += f' ({nickname})'
        return username.strip()

    def response_add(self, request: HttpRequest, obj: TelegramAccount, post_url_continue=None):
        back_url = generate_url_for_model_object(LinkTypes.CHANGE, obj)
        url = generate_url_for_model_object('confirm', obj, params={'back_to': back_url})
        return redirect(url)


admin.site.register(TelegramAccount, TelegramAccountAdmin)
