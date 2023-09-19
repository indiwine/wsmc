from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest, JsonResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse

from social_media.models import SmCredential
from ..social_media import SocialMediaEntities
from ..webdriver import Agent
from ..webdriver.exceptions import WsmcWebDriverLoginError
from ..webdriver.request import Request


class SmCredentialsAdmin(ModelAdmin):
    list_display = ('user_name', 'social_media')
    list_filter = ['social_media']

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super().get_readonly_fields(request, obj)
        return ['social_media']

    async def check_login(self, request: HttpRequest, object_id):
        credential: SmCredential = self.get_object(request, object_id)

        if request.method == "POST":
            login_request = Request([SocialMediaEntities.LOGIN], credential)
            agent = Agent(login_request)
            try:
                await agent.run()
                self.message_user(request, 'Логін пройшов успішно', messages.SUCCESS)
            except WsmcWebDriverLoginError as err:
                self.message_user(request, f'Логін провалився: {err}', messages.ERROR)

            return JsonResponse({"result": "OK"})
        else:
            opts = self.model._meta
            context = {
                **self.admin_site.each_context(request),
                "title": f'Перевірка логіна "{credential}"',
                "post_url": request.get_full_path(),
                "redirect_url": reverse("admin:%s_%s_change" % (opts.app_label, opts.model_name), args=(object_id,))
            }
            return TemplateResponse(request, 'admin/social_media/smcredential/check_login.html', context)

    def get_urls(self):
        ursl = super().get_urls()
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/check-login', self.check_login,
                 name="%s_%s_check_login" % (opts.app_label, opts.model_name))
        ]
        return ursl + additional_urls


admin.site.register(SmCredential, SmCredentialsAdmin)
