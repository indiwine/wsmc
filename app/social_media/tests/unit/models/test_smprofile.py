import datetime

from django.test import TestCase

from social_media.models import SmCredential, SmProfile, SmPost, SmLikes, SmComment
from social_media.social_media import SocialMediaTypes


class TestSmProfile(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.credential = SmCredential.objects.create(id=1, user_name='dummy_1', password='pass', social_media=SocialMediaTypes.VK)

        cls.profile = SmProfile.objects.create(
            credentials=cls.credential,
            oid='123',
            name='test',
            social_media=SocialMediaTypes.VK,
            location='Киев',
        )



    def test_resolve_country_ref(self):
        self.profile.resolve_country_ref('Ukraine')
        self.profile.save()
        self.assertTrue(self.profile.country_ref_id)
        self.assertEqual('ua', self.profile.country_ref.code)

        self.profile.identify_location(structured_mode=True)
        self.assertTrue(self.profile.location_point)
        self.assertTrue(self.profile.location_known)
        self.assertTrue(self.profile.location_precise)



    def test_move_to_junk(self):
        second_profile = SmProfile.objects.create(
            credentials=self.credential,
            oid='456',
            name='test',
            social_media=SocialMediaTypes.VK,
            location='Киев',
        )
        SmPost.objects.create(
            author_object=self.profile,
            origin_object=second_profile,
            social_media=SocialMediaTypes.VK,
            datetime=datetime.datetime.now(),
            sm_post_id='123',
            body='test'
        )
        SmPost.objects.create(
            author_object=second_profile,
            origin_object=self.profile,
            social_media=SocialMediaTypes.VK,
            datetime=datetime.datetime.now(),
            sm_post_id='456',
            body='test'
        )
        SmLikes.objects.create(
            owner=self.profile,
            parent_object=second_profile,
        )

        SmComment.objects.create(
            owner=self.profile,
            post=SmPost.objects.first(),
            datetime=datetime.datetime.now(),
            oid='123',
        )

        self.profile.move_to_junk()
        self.assertTrue(self.profile.in_junk)
        self.assertFalse(SmPost.objects.filter(author=self.profile).exists())
        self.assertFalse(SmLikes.objects.filter(owner=self.profile).exists())
        self.assertFalse(SmComment.objects.filter(owner=self.profile).exists())
