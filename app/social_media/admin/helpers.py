import urllib.parse
from enum import Enum
from typing import Optional, Union, Type

from django.db.models import Model
from django.urls import reverse
from django.utils.safestring import mark_safe


class LinkTypes(Enum):
    CHANGELIST = 'changelist'
    ADD = 'add'
    HISTORY = 'history'
    DELETE = 'delete'
    CHANGE = 'change'


def _extract_page(page: Union[LinkTypes, str]) -> str:
    if isinstance(page, LinkTypes):
        return page.value

    return page


def generate_admin_url(page: Union[LinkTypes, str],
                       app_label: str,
                       model_name: str,
                       args: Optional[tuple] = None,
                       kwargs: Optional[dict] = None,
                       params: Optional[dict] = None) -> str:
    url = reverse(f'admin:{app_label}_{model_name}_{_extract_page(page)}', args=args, kwargs=kwargs)
    if params:
        url += f'?{urllib.parse.urlencode(params)}'

    return url


def generate_url_for_model(
        page: Union[LinkTypes, str],
        model: Type[Model],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        params: Optional[dict] = None) -> str:
    return generate_admin_url(
        page,
        model._meta.app_label,
        model._meta.model_name,
        args,
        kwargs,
        params
    )


def generate_admin_link(
        page: Union[LinkTypes, str],
        app_label: str,
        model_name: str,
        text: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        params: Optional[dict] = None
) -> str:
    url = generate_admin_url(page, app_label, model_name, args, kwargs, params)
    return mark_safe(f'<a href="{url}">{text}</a>')


def generate_link_for_model(
        page: Union[LinkTypes, str],
        model: Type[Model],
        text: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        params: Optional[dict] = None) -> str:
    return generate_admin_link(
        page,
        model._meta.app_label,
        model._meta.model_name,
        text,
        args,
        kwargs,
        params
    )


def generate_link_for_model_object(
        page: Union[LinkTypes, str],
        model: Model,
        text: str,
        kwargs: Optional[dict] = None,
        params: Optional[dict] = None) -> str:
    return generate_admin_link(
        page,
        model._meta.app_label,
        model._meta.model_name,
        text,
        (model.pk,),
        kwargs,
        params
    )
