from datetime import datetime
from typing import Optional

from django.utils import timezone

from social_media.webdriver.options.baseoptions import BaseOptions


class OkOptions(BaseOptions):
    post_date_limit: Optional[datetime] = datetime(2022, 2, 24, tzinfo=timezone.get_current_timezone())
    """
    Maximum date limit for collecting posts
    """

    post_count_limit: Optional[int] = None

    skip_likes_for_known_posts: bool = True
