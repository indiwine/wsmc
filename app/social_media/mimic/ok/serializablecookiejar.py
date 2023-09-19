import base64
import pickle

import aiohttp


class SerializableCookieJar(aiohttp.CookieJar):
    def to_base64(self) -> str:
        binary_data = pickle.dumps(self._cookies, protocol=pickle.HIGHEST_PROTOCOL)

        # Convert binary_data to base64 string
        return base64.b64encode(binary_data).decode('utf-8')

    def from_base64(self, base64_str: str):
        binary_data = base64.b64decode(base64_str)
        self._cookies = pickle.loads(binary_data)
