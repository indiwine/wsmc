from __future__ import annotations

from social_media.models import Suspect, ScreeningReport
from .screening_modules.abstractscreeningmodule import AbstractScreeningModule
from .screening_modules.confidentialinformationscreener import ConfidentialInformationScreener
from .screening_modules.postkeywordscreener import PostKeywordScreener
from .screening_modules.profilelocationscreener import ProfileLocationScreener
from .screeningrequest import ScreeningRequest


class Screener:
    def __init__(self, request: ScreeningRequest):
        self.request = request

    def scan(self):
        self._build_chain().handle(self.request)
        self.request.report.resulting_score = self.request.score
        self.request.report.save()
        return self.request.score

    def _build_chain(self) -> AbstractScreeningModule:
        return ProfileLocationScreener() \
            .set_next(ConfidentialInformationScreener()
                      .set_next(PostKeywordScreener())
                      )

    @staticmethod
    def build(suspect: Suspect) -> Screener:
        report = ScreeningReport(name=f'Перевірка "{suspect.__str__()}"', suspect=suspect)
        report.save()
        return Screener(ScreeningRequest(suspect, report))
