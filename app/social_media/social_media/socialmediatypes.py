from django.db.models import TextChoices


class SocialMediaTypes(TextChoices):
    FB = 'fb', 'Facebook'
    VK = 'vk', 'Вконтакте'
    OK = 'ok', 'Однокласники'
