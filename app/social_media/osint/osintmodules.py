from __future__ import annotations

from typing import Optional

from django.db.models import TextChoices

from telegram_connection.interaction.abstractinteractionrequest import AbstractInteractionRequest
from telegram_connection.interaction.email_check.emailcheckrequest import EmailCheckRequest
from telegram_connection.interaction.name_check.namecheckrequest import NameCheckRequest
from telegram_connection.interaction.phone_check.phonecheckrequest import PhoneCheckRequest
from telegram_connection.interaction.sm_check.smcheckrequest import SmCheckRequest


class OsintModules(TextChoices):
    TG_PHONE_BOT = 'tg_phone_bot', 'Телефон у Telegram ботах'
    TG_EMAIL_BOT = 'tg_email_bot', 'E-Mail у Telegram ботах'
    TG_NAME_BOT = 'tg_name_bot', "Ім'я у Telegram ботах"
    TG_SM_BOT = 'tg_sm_bot', "Соц. мережі у Telegram ботах"
    HOLEHE_EMAIL = 'holehe_email', 'HOLEHE E-Mail'

    @classmethod
    def from_interation_request(cls, request: AbstractInteractionRequest) -> Optional[OsintModules]:
        if isinstance(request, PhoneCheckRequest):
            return cls.TG_PHONE_BOT
        elif isinstance(request, NameCheckRequest):
            return cls.TG_NAME_BOT
        elif isinstance(request, EmailCheckRequest):
            return cls.TG_EMAIL_BOT
        elif isinstance(request, SmCheckRequest):
            return cls.TG_SM_BOT
        return None
