from django.apps import AppConfig
from .ai.loader import load_models


class SocialMediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_media'
    verbose_name = 'WSMC'

    def ready(self):
        load_models()
