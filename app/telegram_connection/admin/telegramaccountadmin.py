import logging

from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.forms import Form, CharField
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from telegram.client import AuthorizationState

from social_media.admin.helpers import generate_url_for_model_object, LinkTypes
from ..admin_pages import CONFIRM_PAGE, LOGOUT_PAGE
from ..agent import TgAgent
from ..models import TelegramAccount

logger = logging.getLogger(__name__)


class OtpForm(Form):
    password = CharField()


class TelegramAccountAdmin(ModelAdmin):
    list_display = ['phone', 'name', 'logged_in']
    readonly_fields = ['name', 'logged_in']
    save_as_continue = False
    filter_horizontal = ['bots_to_use']

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj is not None:
            return fields + ['phone']
        return fields

    def tg_logout(self, request: HttpRequest, object_id):
        account: TelegramAccount = self.get_object(request, object_id)
        agent = TgAgent(account)

        code = agent.login()
        if code == AuthorizationState.READY:
            agent.logout()
            account.logged_in = False
            account.save()
            self.message_user(request, 'Логаут успішний', messages.SUCCESS)
        else:
            self.message_user(request, f'Код: "{code}"', messages.WARNING)

        return redirect(generate_url_for_model_object(LinkTypes.CHANGE, account))

    def confirm_tg_login(self, request: HttpRequest, object_id):
        account: TelegramAccount = self.get_object(request, object_id)
        agent = TgAgent(account)

        code = agent.login()
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
                        agent.tg.send_code(otp_or_pass)
                    elif code == AuthorizationState.WAIT_PASSWORD:
                        agent.tg.send_password(otp_or_pass)
                    else:
                        self.message_user(request, f'Unknown code "{code}" received during login to telegram',
                                          messages.ERROR)
                    user = agent.get_me()
                    account.name = user.account_name
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
            agent.stop()

    def get_urls(self):
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/confirm', self.confirm_tg_login,
                 name='%s_%s_%s' % (opts.app_label, opts.model_name, CONFIRM_PAGE)),
            path('<path:object_id>/logout', self.tg_logout,
                 name='%s_%s_%s' % (opts.app_label, opts.model_name, LOGOUT_PAGE)),
        ]

        return additional_urls + super().get_urls()

    def response_add(self, request: HttpRequest, obj: TelegramAccount, post_url_continue=None):
        back_url = generate_url_for_model_object(LinkTypes.CHANGE, obj)
        url = generate_url_for_model_object(CONFIRM_PAGE, obj, params={'back_to': back_url})
        return redirect(url)


admin.site.register(TelegramAccount, TelegramAccountAdmin)
