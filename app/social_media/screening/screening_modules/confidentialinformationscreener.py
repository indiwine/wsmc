import json
import logging
import re
from dataclasses import dataclass, asdict
from re import Match, Pattern
from typing import Optional, Tuple, List, Callable

import phonenumbers
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException, InvalidStructure, InvalidCountryCode

from .abstractscreeningmodule import AbstractScreeningModule
from .. import ScreeningModules
from ..screeningrequest import ScreeningRequest
from ..types import ConfidentialInformationType
from ...models import SmPost, ScreeningDetail

logger = logging.getLogger(__name__)
PHONE_COUNTRIES = ['RU', 'UA', 'BY', 'KZ']


@dataclass
class ConfidentialInformation:
    type: ConfidentialInformationType
    item: Optional[str] = None
    isValid: bool = False
    isAlike: bool = True
    dict = asdict


ExtractionResultType = Tuple[str, List[ConfidentialInformation]]
ExtractionCb = Callable[[Match], ConfidentialInformation]


class ConfidentialInformationScreener(AbstractScreeningModule):
    def __init__(self):
        self.numbers_pattern = re.compile(r"(?:[\+\(])?(?:[\ \-\–\(\)]*\d){9,15}", re.MULTILINE)
        self.iban_pattern = re.compile(self._generate_iban_pattern('11,30'), re.MULTILINE | re.IGNORECASE)
        self.credit_card_pattern = re.compile(r"\b(?:\d[\ \-]*){16}\b", re.MULTILINE)
        self.special_chars_pattern = re.compile(r"[\ \-\(\)]")

    @staticmethod
    def _generate_iban_pattern(bban_length: str):
        return r"\b[a-z]{2}[\ \-]*\d{2}[\ \-]*(?:[\ \-]*[a-z0-9]){" + str(bban_length) + r"}\b"

    def handle(self, screening_request: ScreeningRequest):
        logging.info('Looking for personal information in post')
        posts = SmPost.objects.only('body').filter(suspect=screening_request.suspect, body__isnull=False) \
            .order_by('-datetime') \
            .iterator(1000)

        for post in posts:
            confidential_information_list = self.look_for_info(post.body)
            if confidential_information_list:
                confidential_information_list_dict = list(
                    map(lambda item: item.__dict__, confidential_information_list))
                logger.debug(
                    f'Confidential information found: {json.dumps(confidential_information_list_dict, indent=2)}')
                detail = ScreeningDetail(
                    report=screening_request.report,
                    content_object=post,
                    module=ScreeningModules.CONFIDENTIAL_INFORMATION,
                    result=confidential_information_list_dict
                )
                detail.save()

        super().handle(screening_request)

    def look_for_info(self, post_body: str) -> List[ConfidentialInformation]:
        body = post_body
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
            normalized = self.special_chars_pattern.sub('', info.item)
            info.isValid, info.isAlike = self._check_phone_number(normalized)
            return info

        return self._do_extract(body, self.numbers_pattern, phone_validation)

    @staticmethod
    def _check_phone_number(phone_number: str) -> Tuple[bool, bool]:
        if phone_number[0] == '+':
            phone = phonenumbers.parse(phone_number)
            return phonenumbers.is_valid_number(phone), phonenumbers.is_possible_number(phone)

        for code in PHONE_COUNTRIES:
            phone = phonenumbers.parse(phone_number, code)
            if phonenumbers.is_valid_number(phone):
                return True, True

        for code in PHONE_COUNTRIES:
            phone = phonenumbers.parse(phone_number, code)
            if phonenumbers.is_possible_number(phone):
                return False, True

        return False, False

    def _look_for_credit_cards(self, body: str) -> ExtractionResultType:
        def card_validation(match: Match) -> ConfidentialInformation:
            info = ConfidentialInformation(
                type=ConfidentialInformationType.CREDIT_CARD,
                item=match.group().strip()
            )
            normalized = self.special_chars_pattern.sub('', info.item)
            info.isValid = self.validate_credit_card(normalized)

            return info

        return self._do_extract(body, self.credit_card_pattern, card_validation)

    def _look_for_iban(self, body: str) -> ExtractionResultType:

        def extract_iban(match: Match) -> Tuple[str, bool]:
            dirty_iban = match.group().strip()
            iban_inst = IBAN(dirty_iban, allow_invalid=True)
            try:
                precise_pattern = re.compile(self._generate_iban_pattern(iban_inst.spec['bban_length']), re.IGNORECASE)
                clean_iban_match = precise_pattern.match(dirty_iban)
                if not clean_iban_match:
                    return dirty_iban, True
                return clean_iban_match.group().strip(), False
            except InvalidCountryCode:
                return dirty_iban, True

        result = []
        result_body = body
        for match in self.iban_pattern.finditer(body):
            confidential_information_item = ConfidentialInformation(type=ConfidentialInformationType.IBAN)
            result.append(confidential_information_item)
            try:
                confidential_information_item.item, is_dirty = extract_iban(match)
                result_body = result_body.replace(confidential_information_item.item, '')

                if is_dirty:
                    confidential_information_item.isAlike = False
                    continue

                IBAN(confidential_information_item.item)
                confidential_information_item.isValid = True
            except SchwiftyException as e:
                if isinstance(e, InvalidStructure):
                    confidential_information_item.isAlike = False

        return result_body, result

    def _do_extract(self, body: str, pattern: Pattern, cb: ExtractionCb) -> ExtractionResultType:
        result = []
        for match in pattern.finditer(body):
            result.append(cb(match))

        result_body = body
        if result:
            result_body = pattern.sub('', body)

        return result_body, result

    @staticmethod
    def validate_credit_card(card_number: str) -> bool:
        """This function validates a credit card number."""
        # 1. Change datatype to list[int]
        card_number = [int(num) for num in card_number]

        # 2. Remove the last digit:
        check_digit = card_number.pop(-1)

        # 3. Reverse the remaining digits:
        card_number.reverse()

        # 4. Double digits at even indices
        card_number = [num * 2 if idx % 2 == 0
                       else num for idx, num in enumerate(card_number)]

        # 5. Subtract 9 at even indices if digit is over 9
        # (or you can add the digits)
        card_number = [num - 9 if idx % 2 == 0 and num > 9
                       else num for idx, num in enumerate(card_number)]

        # 6. Add the checkDigit back to the list:
        card_number.append(check_digit)

        # 7. Sum all digits:
        check_sum = sum(card_number)

        # 8. If checkSum is divisible by 10, it is valid.
        return check_sum % 10 == 0
