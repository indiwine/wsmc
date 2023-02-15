from django.apps import AppConfig
from django.conf import settings
from .ai.loader import load_models


class SocialMediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_media'
    verbose_name = 'WSMC'

    def ready(self):
        if settings.WSMC_LOAD_AI:
            load_models()
