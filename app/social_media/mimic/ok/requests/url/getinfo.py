import dataclasses
from dataclasses import dataclass
from typing import Type, Optional, Union

from social_media.mimic.ok.requests.abstractrequest import GenericRequest, AbstractRequestParams, GenericResponseBody, \
    GenericResponse, RESPONSE_BODY


@dataclass
class UrlGetInfoParams(AbstractRequestParams):
    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)

    url: str


class UrlGetInfoBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.objectId: Optional[int] = None
        self.objectIdEncoded: Optional[str] = None
        """
        Do not use encoded object id, it is not working (at least for groups)
        """
        self.objectIdStr: Optional[str] = None
        self.type: Optional[str] = None
        super().__init__(raw_params)


class UrlGetInfoResponse(GenericResponse[UrlGetInfoBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return UrlGetInfoBody


class UrlGetInfoRequest(GenericRequest[UrlGetInfoParams, None]):
    def __init__(self, url: str):
        super().__init__('url', 'getInfo', UrlGetInfoParams(url=url))

    @staticmethod
    def bound_response_cls() -> Type[GenericResponse]:
        return UrlGetInfoResponse
