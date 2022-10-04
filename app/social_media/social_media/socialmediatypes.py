from enum import Enum


class SocialMediaTypes(Enum):
    FB = 'fb'
    VK = 'vk'
    OK = 'ok'


social_media_model_choices = (
    (SocialMediaTypes.FB.value, 'Facebook'),
    (SocialMediaTypes.VK.value, 'Вконтакте'),
    (SocialMediaTypes.OK.value, 'Однокласники')
)

social_media_model_choices_dict = dict(social_media_model_choices)
