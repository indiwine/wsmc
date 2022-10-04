from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.http import HttpRequest
from django.urls import path

from social_media.models import SuspectSocialMediaAccount, Suspect, SmProfile
from social_media.social_media import SocialMediaEntities
from social_media.webdriver import Request, Agent


class LinkedSmAccounts(StackedInline):
    model = SuspectSocialMediaAccount
    extra = 1


class LinkedSmProfile(StackedInline):
    model = SmProfile

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SuspectAdmin(ModelAdmin):
    inlines = [LinkedSmAccounts, LinkedSmProfile]
    search_fields = ['name']

    def perform_scan(self, request: HttpRequest, object_id):
        suspect: Suspect = self.get_object(request, object_id)
        sm_accounts = SuspectSocialMediaAccount.objects.filter(suspect=suspect)
        for sm_account in sm_accounts:
            collect_request = Request(
                [SocialMediaEntities.LOGIN, SocialMediaEntities.PROFILE],
                sm_account.credentials,
                sm_account
            )
            agent = Agent(collect_request)
            agent.run()

    def get_urls(self):
        ursl = super().get_urls()
        opts = self.model._meta
        additional_urls = [
            path('<path:object_id>/perform-scan', self.perform_scan,
                 name='%s_%s_perform_scan' % (opts.app_label, opts.model_name))
        ]
        return ursl + additional_urls


admin.site.register(Suspect, SuspectAdmin)
