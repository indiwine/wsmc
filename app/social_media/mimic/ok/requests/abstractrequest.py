from __future__ import annotations

import abc
from abc import ABC
from enum import Enum
from typing import TypeVar, Generic, Type, Optional, Union, TypedDict


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


class AbstractRequestParams(ABC):
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

    @property
    def dotted_method_name(self) -> str:
        return f'{self.method_group}.{self.method}'

    @property
    def pathed_method_name(self) -> str:
        return f'{self.method_group}/{self.method}'


class GenericResponseBody(AbstractResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.raw_params = raw_params

        if isinstance(raw_params, dict):
            for key, value in raw_params.items():
                setattr(self, key, value)


class GenericResponse(AbstractResponse):
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
        body_cls = self.get_body_class()
        self.body = body_cls(raw_response)


class GenericRequest(AbstractRequest):
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
