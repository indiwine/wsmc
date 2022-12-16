import re
import phonenumbers
from dataclasses import dataclass, asdict
from re import Match, Pattern
from typing import Optional, Tuple, List, Generator, Callable

from django.db.models import TextChoices
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException, InvalidStructure

from .abstractscreeningmodule import AbstractScreeningModule
from ..screeningrequest import ScreeningRequest
from ...models import SmPost


class ConfidentialInformationType(TextChoices):
    PHONE = 'phone', 'Телефон'
    IBAN = 'iban', 'Рахунок IBAN'
    CREDIT_CARD = 'card', 'Банківська картка'


@dataclass
class ConfidentialInformation:
    type: ConfidentialInformationType
    item: str
    isValid: bool = False
    isAlike: bool = True
    extra: Optional[str] = None
    dict = asdict


ExtractionResultType = Tuple[str, List[ConfidentialInformation]]
ExtractionCb = Callable[[Match], ConfidentialInformation]


class ConfidentialInformationScreener(AbstractScreeningModule):
    def __init__(self):
        self.numbers_pattern = re.compile(r"(?:[\+\(])?(?:[\ \-\–\(\)]*\d){6,15}", re.MULTILINE)
        self.iban_pattern = re.compile(r"\b[a-z]{2}[\ \-]*\d{2}[\ \-]*(?:[\ \-]*[a-z0-9]){11,30}\b",
                                       re.MULTILINE | re.IGNORECASE)
        self.credit_card_pattern = re.compile(r"\b(?:\d[\ \-]*){13,16}\b", re.MULTILINE)
        self.special_chars_pattern = re.compile(r"[\ \-\(\)]")

    def handle(self, screening_request: ScreeningRequest):
        posts = SmPost.objects.only('body').filter(suspect=screening_request.suspect, body__isnull=False) \
            .order_by('-datetime') \
            .iterator(1000)
        for post in posts:
            pass

    def _look_for_info(self, post: SmPost) -> List[ConfidentialInformation]:
        body = post.body
        body, ibans = self._look_for_iban(body)
        body, cards = self._look_for_credit_cards(body)
        _, phones = self._look_for_phone_numbers(body)

        return ibans + cards + phones

    def _look_for_phone_numbers(self, body: str) -> ExtractionResultType:
        def phone_validation(match: Match) -> ConfidentialInformation:
            info = ConfidentialInformation(
                type=ConfidentialInformationType.PHONE,
                item=match.group().strip()
            )
            norm = self.special_chars_pattern.sub('', info.item)

            return info

        return self._do_extract(body, self.numbers_pattern, phone_validation)

    def _look_for_credit_cards(self, body: str) -> ExtractionResultType:
        def card_validation(match: Match) -> ConfidentialInformation:
            info = ConfidentialInformation(
                type=ConfidentialInformationType.CREDIT_CARD,
                item=match.group().strip()
            )
            norm = self.special_chars_pattern.sub('', info.item)

            return info

        return self._do_extract(body, self.credit_card_pattern, card_validation)

    def _look_for_iban(self, body: str) -> ExtractionResultType:
        def iban_validation(match: Match) -> ConfidentialInformation:
            info = ConfidentialInformation(
                type=ConfidentialInformationType.IBAN,
                item=match.group().strip()
            )
            norm = self.special_chars_pattern.sub('', info.item)
            try:
                IBAN(norm)
                info.isValid = True
            except SchwiftyException as e:
                if isinstance(e, InvalidStructure):
                    info.isAlike = False
                info.extra = str(e)

            return info

        return self._do_extract(body, self.iban_pattern, iban_validation)

    def _do_extract(self, body: str, pattern: Pattern, cb: ExtractionCb) -> ExtractionResultType:
        result = []
        try:
            for match in self._do_iter_and_replace(body, pattern):
                result.append(cb(match))
        except StopIteration as e:
            return e.value, result

    @staticmethod
    def _do_iter_and_replace(body: str, pattern: Pattern) -> Generator[Match, None, str]:
        for match in pattern.finditer(body):
            yield match

        return pattern.sub('', body)
