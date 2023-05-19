import datetime

from django.conf import settings
from django.test import SimpleTestCase
from pathlib import Path

from social_media.dtos import SmGroupDto, SmPostDto, SmPostImageDto, AuthorDto, SmProfileDto, SmProfileMetadata
from social_media.social_media import SocialMediaTypes
from social_media.webdriver.common import date_time_parse
from social_media.webdriver.driverbuilder import DriverBuilder
from social_media.webdriver.exceptions import WsmcWebDriverProfileNotFoundException
from social_media.webdriver.link_builders.vk.vklinkbuilder import VkLinkBuilder
from social_media.webdriver.page_objects.vk.vkgrouppage import VkGroupPage
from social_media.webdriver.page_objects.vk.vkloginpage import VkLoginPage
from social_media.webdriver.page_objects.vk.vkprofilepage import VkProfilePage
from social_media.webdriver.page_objects.vk.vksinglepostpage import VkSinglePostPage


class TestVkDataCollection(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = DriverBuilder.build()
        VkLoginPage(cls.driver, VkLinkBuilder.build('')).perform_login(user_name=settings.TEST_VK_LOGIN,
                                                                       password=settings.TEST_VK_PASSWORD)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()


    def test_group_info_collection(self):
        group_url = 'https://vk.com/officialpages'
        expected_dto = SmGroupDto(
            permalink='https://vk.com/public22079806',
            oid='22079806',
            name='Официальные страницы ВКонтакте',
            social_media=SocialMediaTypes.VK
        )

        group_page_object = VkGroupPage(self.driver, VkLinkBuilder.build_group(group_url))
        group_dto = group_page_object.collect_group()
        self.assertIsInstance(group_dto, SmGroupDto)
        self.assertEqual(group_dto, expected_dto)
        print(group_dto)

    def test_post_info_collection(self):
        page_url = 'https://vk.com/wall-22079806_206330'

        expected_dto = SmPostDto(
            author=AuthorDto(
                oid='22079806',
                url='https://vk.com/officialpages',
                name='Официальные страницы ВКонтакте',
                is_group=True
            ),
            datetime=datetime.datetime(2023, 3, 28, 12, 43),
            sm_post_id='-22079806_206330',
            social_media=SocialMediaTypes.VK,
            body='Почувствуйте себя участниками интеллектуального шоу! Запускайте сервис «Умнее всех» и отвечайте на '
                 'вопросы по эрудиции от телеканала ПЯТНИЦА! Каждую неделю вы можете выиграть планшет, наушники и '
                 'другие призы.\n\nПо вторникам в 19:00 шоу «Умнее всех» можно смотреть по телевизору, а ВКонтакте — '
                 'играть и сражаться за призы. Новые вопросы в мини-приложении будут появляться каждую '
                 'неделю.\n\nОткрывайте сервис и отвечайте на вопросы из разных областей знаний!',
        )

        expected_image = SmPostImageDto(
            oid='-22079806_457251297'
        )

        single_post_page_object = VkSinglePostPage(self.driver, VkLinkBuilder.build_group(page_url))
        post_object = single_post_page_object.get_post_page_object(page_url)

        post_reactions_object = post_object.get_post_reactions_object()
        total_likes = post_reactions_object.likes_count()
        del post_reactions_object

        post_dto = post_object.collect()
        likes = list(post_object.collect_likes())
        print(post_dto)
        print(likes)

        self.assertIsInstance(post_dto, SmPostDto)
        self.assertEqual(expected_dto.author, post_dto.author)
        self.assertEqual(post_dto.sm_post_id, expected_dto.sm_post_id, 'Incorrect post id')
        self.assertEqual(post_dto.social_media, expected_dto.social_media, 'Incorrect social media')
        self.assertEqual(post_dto.body, expected_dto.body, 'Incorrect post body')
        self.assertTrue(post_dto.datetime)

        self.assertEqual(1, len(post_dto.images), 'Number of images does not match')

        image = post_dto.images[0]
        self.assertEqual(image.oid, expected_image.oid, 'Image id doesn\'t mathc')
        self.assertTrue(image.url)

        self.assertEqual(total_likes, len(likes), 'Number of collected likes is different')

    def test_group_navigation_and_post_collection(self):
        group_url = 'https://vk.com/officialpages'
        posts_per_page = 20

        group_page_object = VkGroupPage(self.driver, VkLinkBuilder.build_group(group_url))
        group_page_object.go_to_group()

        wall_object = group_page_object.go_to_wall()
        has_posts = wall_object.wait_for_posts()
        self.assertTrue(has_posts, 'Posts cannot be found')
        posts = []
        for post_object in wall_object.collect_posts(0):
            post_dto = post_object.collect()
            self.assertIsInstance(post_dto, SmPostDto)
            post_reactions_object = post_object.get_post_reactions_object()
            total_likes = post_reactions_object.likes_count()
            post_likes = list(post_object.collect_likes())
            posts.append(post_dto)

        print(posts)
        self.assertEqual(posts_per_page, len(posts), 'number of posts')

    def test_profile_collection(self):
        profile_url = 'https://vk.com/durov'
        profile_page_object = VkProfilePage(self.driver, VkLinkBuilder.build(profile_url))
        profile_dto = profile_page_object.collect_profile()

        expected_dto = SmProfileDto(
            oid='1',
            birthdate=date_time_parse('10.10.1984'),
            name='Павел Дуров',
            country='Россия',
            domain='durov',
            location='Санкт-Петербург',
            university='СПбГУ',
            metadata=SmProfileMetadata(
                site='http://t.me/durov',
                twitter='durov'
            )
        )
        print(profile_dto)
        self.assertEqual(profile_dto, expected_dto)

    def test_disabled_profile(self):
        profile_url = 'https://vk.com/id114551834'
        profile_page_object = VkProfilePage(self.driver, VkLinkBuilder.build(profile_url))
        profile_dto = profile_page_object.collect_profile()
        print(profile_dto)

    def test_screenshot(self):
        profile_url = 'https://vk.com/id203133326'
        profile_page_object = VkProfilePage(self.driver, VkLinkBuilder.build(profile_url))
        profile_page_object.navigate_if_necessary()
        file_path = self.driver.save_screenshot_safe('test')

        self.assertIsInstance(file_path, Path)
        self.assertTrue(file_path.is_file())
        self.assertTrue(file_path.exists())

    def test_non_standard_chars(self):
        profile_url = 'https://vk.com/id296682879'
        expected_dto = SmProfileDto(
            oid='296682879',
            birthdate=date_time_parse('28.07.1985'),
            name='Гарик Балоян',
            country='Армения',
            domain='id296682879',
            location=None,
            university='ՇՊՀ (ШГУ им. Налбандяна, бывш. ԳՊՄԻ Մ.Նալբանդյանի անվան, ГГПИ им. Налбандяна) Սոցիալական գիտությունների և իրավունքի ֆակուլտետը (Факультет социальных наук и права)',
            home_town='Петропавловск-Камчатский🌋',
            metadata=None
        )

        profile_page_object = VkProfilePage(self.driver, VkLinkBuilder.build(profile_url))
        profile_dto = profile_page_object.collect_profile()
        print(profile_dto)
        self.assertEqual(profile_dto, expected_dto)

    def test_not_found_profile(self):
        profile_url = 'https://vk.com/id729303074'
        profile_page_object = VkProfilePage(self.driver, VkLinkBuilder.build(profile_url))
        self.assertRaises(WsmcWebDriverProfileNotFoundException, profile_page_object.collect_profile)
