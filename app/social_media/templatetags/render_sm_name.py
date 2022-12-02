from django import template
from django.template.defaultfilters import stringfilter

from social_media.social_media import SocialMediaTypes

register = template.Library()


@register.filter
@stringfilter
def render_sm_name(value):
    return SocialMediaTypes(value).label
