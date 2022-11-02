# from django.contrib import admin
# from django.urls import path
# from telegram.client import Telegram
# from django.conf import settings
#
# class CustomAdminSite(admin.AdminSite):
#     def link_tg_device(self, request):
#         tg = Telegram(
#             api_id=settings.TELEGRAM_API_ID,
#             api_hash=settings.TELEGRAM_API_HASH,
#             phone=settings.TELEGRAM_PHONE,
#             database_encryption_key=settings.TELEGRAM_DATABASE_ENCRYPTION_KEY,
#             device_model='WSMC App',
#         )
#         tg.login(blocking=False)
#
#
#     def get_urls(self):
#         additional_urls = [
#             path('link-tg', self.link_tg_device, name='link-tg')
#         ]
#
#         return additional_urls + super().get_urls()

from .telegramaccountadmin import TelegramAccountAdmin