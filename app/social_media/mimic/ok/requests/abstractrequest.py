from __future__ import annotations

import abc
import json
from abc import ABC
from enum import Enum
from typing import TypeVar, Generic, Type, Optional, Union, TypedDict

from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.device import AndroidDevice


class OkRequestHttpMethod(Enum):
    GET = 'g'
    POST = 'p'


class AbstractCustomPayloadEncoderMixin(ABC):
    @abc.abstractmethod
    def encode(self, payload: dict) -> bytes:
        """
        Encode payload to string
        """
        pass

    def get_content_type(self) -> str:
        """
        Get content type of encoded payload
        """
        return 'application/octet-stream'

    def get_content_encoding(self) -> Optional[str]:
        """
        Get content encoding of encoded payload
        """
        return None


class AbstractRequestParams(ABC):
    def configure_before_send(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions):
        """
        Configure params before sending

        @param device:
        @param auth_options:
        @return:
        """
        pass

    @abc.abstractmethod
    def to_execute_dict(self) -> dict:
        """
        Convert params to a dict method to use with
        """
        pass


class AbstractResponseBody(ABC):
    @abc.abstractmethod
    def __init__(self, raw_params: Union[dict, list]):
        pass


PARAMS = TypeVar('PARAMS', bound=AbstractRequestParams)
RESPONSE_BODY = TypeVar('RESPONSE_BODY', bound=AbstractResponseBody)
RESPONSE = TypeVar('RESPONSE', bound=AbstractResponseBody)


class AbstractResponse(ABC, Generic[RESPONSE_BODY]):
    def __init__(self, request: AbstractRequest):
        self.request = request

    @staticmethod
    @abc.abstractmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        pass

    @abc.abstractmethod
    def get_body(self) -> RESPONSE_BODY:
        pass

    @abc.abstractmethod
    def set_from_raw(self, raw_response: Union[dict, list]):
        pass


class AbstractRequest(ABC, Generic[PARAMS]):

    @property
    @abc.abstractmethod
    def http_method(self) -> OkRequestHttpMethod:
        pass

    @property
    @abc.abstractmethod
    def method(self) -> str:
        pass

    @staticmethod
    @abc.abstractmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        pass

    @property
    @abc.abstractmethod
    def method_group(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def params(self) -> PARAMS:
        pass

    @abc.abstractmethod
    def to_execute_dict(self) -> dict:
        pass
    @abc.abstractmethod
    def is_json(self) -> bool:
        """
        Is request should be sent as json or as x-www-form-urlencoded
        NOTE: This is only applicable for POST requests and only without AbstractCustomPayloadEncoderMixin
        """
        pass

    def configure(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions):
        """
        Configure request and its own parameters before sending
        @param device:
        @param auth_options:
        @return:
        """
        self.params.configure_before_send(device, auth_options)

    @property
    def dotted_method_name(self) -> str:
        return f'{self.method_group}.{self.method}'

    @property
    def pathed_method_name(self) -> str:
        return f'{self.method_group}/{self.method}'

    def __str__(self):
        return f'{self.__class__.__name__}: {self.dotted_method_name}'


class GenericResponseBody(AbstractResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.raw_params = raw_params

        if isinstance(raw_params, dict):
            for key, value in raw_params.items():
                setattr(self, key, value)

    def __str__(self):
        return f'{self.__class__.__name__}: {json.dumps(self.raw_params)}'


class GenericResponse(AbstractResponse[RESPONSE_BODY]):
    body: Optional[RESPONSE_BODY] = None
    raw_body: Optional[Union[dict, list]] = None

    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return GenericResponseBody

    def get_body(self) -> RESPONSE_BODY:
        if not self.body:
            raise RuntimeError('Body hase not been set yet')
        return self.body

    def set_from_raw(self, raw_response: Union[dict, list]):
        self.raw_body = raw_response
        self.create_and_set_body(raw_response)

    def create_body_instance(self, raw_response: Union[dict, list]) -> RESPONSE_BODY:
        body_cls = self.get_body_class()
        return body_cls(raw_response)

    def create_and_set_body(self, raw_response: Union[dict, list]):
        self.body = self.create_body_instance(raw_response)




class GenericRequest(AbstractRequest[PARAMS]):

    def is_json(self) -> bool:
        return True

    @property
    def http_method(self) -> OkRequestHttpMethod:
        return OkRequestHttpMethod.POST

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return GenericResponse

    @property
    def method_group(self) -> str:
        return self._method_group

    def to_execute_dict(self) -> dict:
        return self.params.to_execute_dict()

    @property
    def method(self) -> str:
        return self._method

    @property
    def params(self) -> PARAMS:
        return self._params

    def __init__(self, method_group: str, method: str, params: AbstractRequestParams):
        self._method = method
        self._method_group = method_group
        self._params = params
