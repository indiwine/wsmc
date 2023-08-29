from __future__ import annotations
import dataclasses
from typing import Optional, TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from social_media.mimic.ok.requests.auth.login import LoginResponseBody


@dataclasses.dataclass
class OkHttpClientAuthOptions:
    application_key: str = settings.MIMIC_OK_APP_KEY
    session_key: Optional[str] = None
    screen: Optional[str] = None
    current_login_data: Optional[LoginResponseBody] = None
