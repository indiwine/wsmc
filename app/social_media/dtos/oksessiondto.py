from typing import Optional

import dataclasses_json

from social_media.common import nested_dataclass
from social_media.mimic.ok.devices import AndroidDevice


@dataclasses_json.dataclass_json
@nested_dataclass
class OkSessionDto:
    uid: str
    session_key: str
    session_secret_key: str
    auth_token: str
    api_server: str
    auth_sig: str
    activated_profile: bool
    auth_hash: str
    cookie_jar: Optional[str] = None
    device: Optional[AndroidDevice] = None
