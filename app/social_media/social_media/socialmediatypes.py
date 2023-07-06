from __future__ import annotations

from urllib.parse import urlparse

from django.db.models import TextChoices

from social_media.exceptions import UnknownSocialMediaType


class SocialMediaTypes(TextChoices):
    FB = 'fb', 'Facebook'
    VK = 'vk', 'Вконтакте'
    OK = 'ok', 'Однокласники'

    @classmethod
    def _get_map(cls):
        return {
            cls.VK: ['vk.com', 'vk.ru'],
            cls.FB: ['facebook.com', 'www.facebook.com', 'fb.com'],
            cls.OK: ['ok.ru']
        }

    @classmethod
    def from_url(cls, url: str) -> SocialMediaTypes:
        """
        Resolve given URL into a social media type

        @raise UnknownSocialMediaType in case of URL cannot be resolved
        @param url:
        @return:
        """
        o = urlparse(url)
        hostname_to_find = o.hostname
        hostname_map = cls._get_map()
        for sm_type, hostname_list in hostname_map.items():
            filtered_hosts = filter(lambda item: item == hostname_to_find, hostname_list)
            if len(list(filtered_hosts)) > 0:
                return sm_type

        raise UnknownSocialMediaType(f'Cannot determent social media type of an url "{url}"')
