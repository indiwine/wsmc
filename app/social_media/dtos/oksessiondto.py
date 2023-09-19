import dataclasses
from typing import Optional

import dataclasses_json



@dataclasses_json.dataclass_json
@dataclasses.dataclass
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
