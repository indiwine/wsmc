import json
from typing import List

from django import template

from social_media.admin.helpers import convert_vata_prediction_to_w3c
from social_media.ai.models.vatapredictionitem import VataPredictionItem

register = template.Library()


@register.filter
def vata_to_annotation(value: List[VataPredictionItem | dict]):
    return json.dumps(convert_vata_prediction_to_w3c(value))
