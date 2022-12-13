from __future__ import annotations

from typing import Optional, List

from django.conf import settings
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.db.models import QuerySet

from social_media.models import SmPost, BlackPhrase, ScreeningDetail
from .abstractscreeningmodule import AbstractScreeningModule
from ..screeningmodules import ScreeningModules
from ..screeningrequest import ScreeningRequest


class PostKeywordScreener(AbstractScreeningModule):
    _black_phrases_query_set: Optional[QuerySet[BlackPhrase]] = None

    def handle(self, screening_request: ScreeningRequest):
        self._black_phrases_query_set = self._load_keywords()
        posts = SmPost.objects.only().filter(suspect=screening_request.suspect, body__isnull=False) \
            .order_by('-datetime') \
            .iterator(1000)
        for post in posts:
            found_matches = self._check_against_phrases(post)
            if len(found_matches) > 0:
                for match in found_matches:
                    screening_request.score += match['score']

                detail = ScreeningDetail(
                    report=screening_request.report,
                    content_object=post,
                    module=ScreeningModules.POSTS_KEYWORD,
                    result=found_matches
                )
                detail.save()

        super().handle(screening_request)

    @staticmethod
    def _load_keywords():
        return BlackPhrase.objects.all()

    def _check_against_phrases(self, post: SmPost) -> List[dict]:
        result = []
        for phrase in self._black_phrases_query_set:
            query = SearchQuery(phrase.phrase, config=settings.PG_SEARCH_LANG, search_type='websearch')
            headline = SearchHeadline('body',
                                      query,
                                      config=settings.PG_SEARCH_LANG,
                                      start_sel='<span>',
                                      stop_sel='</span>',
                                      fragment_delimiter='...',
                                      max_fragments=50
                                      )
            found_post = SmPost.objects.annotate(headline=headline).filter(id=post.id, search_vector=query).first()
            if found_post:
                result.append({
                    'request': phrase.phrase,
                    'score': 1,
                    'headline': found_post.headline
                })

        return result
