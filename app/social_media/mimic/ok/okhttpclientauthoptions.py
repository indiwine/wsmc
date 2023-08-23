import dataclasses
from typing import Optional

from django.conf import settings


@dataclasses.dataclass
class OkHttpClientAuthOptions:
    application_key: str = settings.MIMIC_OK_APP_KEY
    session_key: Optional[str] = None
    screen: Optional[str] = None
