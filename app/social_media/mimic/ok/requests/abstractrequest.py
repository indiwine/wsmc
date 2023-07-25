import abc
from abc import ABC
from typing import TypeVar, Generic, Type, Optional


class AbstractRequestParams(ABC):
    @abc.abstractmethod
    def to_execute_dict(self) -> dict:
        """
        Convert params to a dict method to use with
        """
        pass


class AbstractResponseBody(ABC):
    @abc.abstractmethod
    def __init__(self, raw_params: dict):
        pass


PARAMS = TypeVar('PARAMS', bound=AbstractRequestParams)
RESPONSE_BODY = TypeVar('RESPONSE_BODY', bound=AbstractResponseBody)


class AbstractResponse(ABC, Generic[RESPONSE_BODY]):

    @staticmethod
    @abc.abstractmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        pass

    @abc.abstractmethod
    def get_body(self) -> RESPONSE_BODY:
        pass

    @abc.abstractmethod
    def set_from_raw(self, raw_response: dict):
        pass


class AbstractRequest(ABC, Generic[PARAMS]):

    @abc.abstractmethod
    @property
    def method(self) -> str:
        pass

    @staticmethod
    @abc.abstractmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        pass

    @abc.abstractmethod
    @property
    def method_group(self) -> str:
        pass

    @abc.abstractmethod
    @property
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
    def __init__(self, raw_params: dict):
        for key, value in raw_params.items():
            setattr(self, key, value)


class GenericResponse(AbstractResponse):
    _body: Optional[RESPONSE_BODY] = None
    raw_body: Optional[dict] = None

    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return GenericResponseBody

    def get_body(self) -> RESPONSE_BODY:
        if not self._body:
            raise RuntimeError('Body hase not been set yet')
        return self._body

    def set_from_raw(self, raw_response: dict):
        self.raw_body = raw_response
        body_cls = self.get_body_class()
        self._body = body_cls(raw_response)


class GenericRequest(AbstractRequest):
    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return GenericResponse

    @property
    def method_group(self) -> str:
        return self._method_group

    def to_execute_dict(self) -> dict:
        return {
            self.dotted_method_name: {
                "params": self.params.to_execute_dict()
            }
        }

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
