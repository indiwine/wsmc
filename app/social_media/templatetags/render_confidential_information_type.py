from django import template
from django.template.defaultfilters import stringfilter

from social_media.screening.types import ConfidentialInformationType

register = template.Library()


@register.filter
@stringfilter
def render_confidential_information_type(value):
    return ConfidentialInformationType(value).label
