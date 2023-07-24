import abc
from abc import ABC
from typing import TypeVar, Generic, Union


class AbstractRequestParams(ABC):
    @abc.abstractmethod
    def to_execute_dict(self) -> dict:
        """
        Convert params to a dict method to use with
        """
        pass


PARAMS = TypeVar('PARAMS', bound=AbstractRequestParams)


class AbstractRequest(ABC, Generic[PARAMS]):

    @abc.abstractmethod
    @property
    def method(self) -> str:
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


class AbstractResponse(ABC):
    pass


class GenericRequest(AbstractRequest):
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
