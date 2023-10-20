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
    """
    Maximum number of posts to collect. If None, no limit is applied
    """

    skip_likes_for_known_posts: bool = True
    """
    Do not collect likes for posts that are already in the database
    """

    discover_profiles_limit: Optional[int] = None
    """
    Maximum number of profiles to discover. If None, no limit is applied
    """

    use_login_jitter: bool = True
    """
    Use login jitter. A random delay will be added before login.
    """
