import base64
import json
import xml.etree.ElementTree as ET
from abc import abstractmethod, ABC
from typing import Generator
from urllib.parse import parse_qsl, urlencode, quote

import zlib

COMPRESSION_LEVEL = 9
COMPRESSION_WBITS = 16 + zlib.MAX_WBITS

class AbstractRequestsReader(ABC):
    @abstractmethod
    def read(self, path: str) -> Generator[bytes, None, None]:
        """
        Read requests from a file or directory
        @param path: path to file
        @return: body of requests
        """
        pass


class BurpSuiteRequestsReader(AbstractRequestsReader):
    def read(self, path: str) -> Generator[bytes, None, None]:
        """
        @type path: path to xml file exported from burp suite
        """
        tree = ET.parse(path)
        root = tree.getroot()
        for item in root.findall('item'):
            yield self._extract_body(self._decode_request(item.find('request').text))

    def _decode_request(self, request: str) -> bytes:
        return base64.b64decode(request)

    def _extract_body(self, request: bytes) -> bytes:
        return request.split(b'\r\n\r\n', 1)[1]


class OkLogStreamDecoder:
    """
    Decoder of Ok log stream.

    Decodes zlib compressed urlencoded data into dict.
    """
    def __init__(self, reader: AbstractRequestsReader):
        self.reader = reader

    def decode(self, path: str) -> Generator[dict, None, None]:
        """
        Decode requests from a file using reader and yield decoded requests as dicts
        @param path:
        """
        for request in self.reader.read(path):
            yield self.decode_request(request)

    def decode_request(self, request: bytes) -> dict:
        url_encoded_body = self.decode_zlib(request)
        return self._parse_request(url_encoded_body)

    @staticmethod
    def decode_zlib(body: bytes) -> str:
        """
        Decode zlib compressed data into string
        @param body: zlib compressed data
        @return: decoded string
        """
        return zlib.decompress(body, COMPRESSION_WBITS).decode('utf-8')

    @staticmethod
    def _parse_request(request: str) -> dict:
        items = dict(parse_qsl(request))
        items['data'] = json.loads(items['data'])
        return items


class OkLogStreamEncoder:
    """
    Encoder of Ok log stream.

    Encodes dict back into zlib compressed urlencoded data.
    It's not byte perfect, but it works.
    """
    def encode(self, data: dict) -> bytes:
        """
        Encode data into zlib compressed urlencoded data

        @param data:
        @return:
        """
        return self._encode_request(data)

    def to_urlencoded(self, data: dict) -> bytes:
        """
        Encode data into urlencoded bytes without zlib compression
        @param data:
        @return:
        """
        return self._encode_form(self._pack_json(data))

    @staticmethod
    def _pack_json(data: dict) -> dict:
        result = data.copy()

        if 'data' in data and not isinstance(data['data'], str):
            result['data'] = json.dumps(data['data'], indent=None, separators=(',', ':'))

        return result

    @staticmethod
    def _encode_form(data: dict) -> bytes:
        return urlencode(data, quote_via=quote).encode('utf-8')

    @staticmethod
    def encode_zlib(data_to_compress: bytes) -> bytes:
        """
        Encode data into zlib compressed bytes
        @param data_to_compress:
        @return:
        """
        compressor = zlib.compressobj(
            COMPRESSION_LEVEL,
            zlib.DEFLATED,
            COMPRESSION_WBITS,
            zlib.DEF_MEM_LEVEL,
            zlib.Z_DEFAULT_STRATEGY
        )

        compressed_data = compressor.compress(data_to_compress)
        compressed_data += compressor.flush()
        return compressed_data

    @classmethod
    def _encode_request(cls, data: dict) -> bytes:
        return cls.encode_zlib(cls._encode_form(cls._pack_json(data)))
