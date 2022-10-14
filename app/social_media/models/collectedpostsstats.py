from __future__ import annotations

from datetime import date
from typing import Generator

from django.db.models import Model, PositiveIntegerField, DateField, ForeignKey, CASCADE, BooleanField, Index, Manager

from social_media.models import SuspectSocialMediaAccount


class CollectedPostsStatsManager(Manager):
    def posts_to_check_generator(self, suspect_account: SuspectSocialMediaAccount) -> Generator[
        CollectedPostsStats, None, None]:
        for date_to_check in self._date_generator():
            try:
                stat = self.get(suspect_account=suspect_account, date=date_to_check)
                if stat.finished:
                    continue
            except CollectedPostsStats.DoesNotExist:
                stat = CollectedPostsStats(suspect_account=suspect_account, date=date_to_check)

            yield stat

    def _date_generator(self) -> Generator[date, None, None]:
        now = date.today()
        for year in range(now.year, 2007, -1):
            check_year = date(year, 1, 1)
            start_month = 12
            if now.year == year:
                start_month = now.month
            for month in range(start_month, 1, -1):
                yield check_year.replace(month=month)


class CollectedPostsStats(Model):
    suspect_account = ForeignKey(SuspectSocialMediaAccount, on_delete=CASCADE)
    found = PositiveIntegerField(default=0)
    skipped = PositiveIntegerField(default=0)
    date = DateField()
    finished = BooleanField(default=False)
    objects = CollectedPostsStatsManager()

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def is_current_month(self) -> bool:
        current_month = date.today().replace(day=1)
        return self.date == current_month

    class Meta:
        indexes = [
            Index(fields=['suspect_account', 'date', 'finished'])
        ]
