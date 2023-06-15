from datetime import datetime
from typing import Optional

from django.utils import timezone

from .baseoptions import BaseOptions


class VkOptions(BaseOptions):
    post_date_limit: Optional[datetime] = datetime(2022, 2, 24, tzinfo=timezone.get_current_timezone())
    """
    Maximum date limit for collecting posts
    """

    post_do_load_latest: bool = True
    """
    Should collector try to find latest posts.
    
    If false, collector will immediately skip to last known offset
    """

    post_count_limit: Optional[int] = None
    """
    Limit number of posts collected
    """

    login_use_jitter = True

    def configure_for_retry(self):
        self.post_do_load_latest = False
