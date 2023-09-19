from django.test import SimpleTestCase

from social_media.exceptions import UnknownSocialMediaType
from social_media.social_media import SocialMediaTypes


class TestSocialMediaTypes(SimpleTestCase):

    def test_vk_type_resolver(self):
        url = 'https://vk.com/some_group?param=1&param=2'
        resolved_type = SocialMediaTypes.from_url(url)
        self.assertCountEqual(SocialMediaTypes.VK, resolved_type)

    def test_fb_type_resolver(self):
        url = 'https://www.facebook.com/groups/Kiev.Ukraine/'
        resolved_type = SocialMediaTypes.from_url(url)
        self.assertCountEqual(SocialMediaTypes.FB, resolved_type)

    def test_ok_type_resolver(self):
        url = 'https://ok.ru/b10.manstoys'
        resolved_type = SocialMediaTypes.from_url(url)
        self.assertCountEqual(SocialMediaTypes.OK, resolved_type)

    def test_unknown_url(self):
        url = 'https://google.com'

        def do_resolve():
            SocialMediaTypes.from_url(url)

        self.assertRaises(UnknownSocialMediaType, do_resolve)

    def test_invalid_url(self):
        url = 'bla bla bla'

        def do_resolve():
            SocialMediaTypes.from_url(url)

        self.assertRaises(UnknownSocialMediaType, do_resolve)



