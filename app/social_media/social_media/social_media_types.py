from enum import Enum


class SocialMediaTypes(Enum):
    FB = 'fb'
    VK = 'vk'
    OK = 'ok'


social_media_model_choices = (
    ('fb', 'Facebook'),
    ('vk', 'Вконтакте'),
    ('ok', 'Однокласники')
)

social_media_model_choices_dict = dict(social_media_model_choices)
