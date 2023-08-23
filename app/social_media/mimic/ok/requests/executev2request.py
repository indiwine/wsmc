import json
from typing import List, Type, Union

from .abstractrequest import AbstractRequest, PARAMS, AbstractRequestParams, AbstractResponse, RESPONSE_BODY, \
    GenericResponse, GenericResponseBody, OkRequestHttpMethod
from ..exceptions import OkResponseNotFoundException


class BatchExecuteParams(AbstractRequestParams):
    request_storage: List[AbstractRequest] = []


    def configure_before_send(self, device, auth_options):
        for req in self.request_storage:
            req.configure(device, auth_options)

    def get_request_by_index(self, index: int) -> AbstractRequest:
        return self.request_storage[index]

    def to_execute_dict(self) -> dict:
        result = []

        for req in self.request_storage:
            result.append({
                req.dotted_method_name: {
                    "params": req.params.to_execute_dict()
                }
            })

        return {
            'methods': json.dumps(result)
        }


class ExecuteV2ResponseBody(GenericResponseBody):
    responses_batch: List[AbstractResponse] = []


class ExecuteV2Response(GenericResponse):

    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return ExecuteV2ResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        assert isinstance(raw_response, list), 'We are expecting list over here'
        response_body: ExecuteV2ResponseBody = self.get_body_class()(raw_response)
        batch_params: BatchExecuteParams = self.request.params

        for index, response_item in enumerate(raw_response):
            batched_request = batch_params.get_request_by_index(index)
            batched_response = batched_request.bound_response_cls()(batched_request)
            batched_response.set_from_raw(response_item['ok'])
            response_body.responses_batch.append(batched_response)

        self.body = response_body

    def find_response_by_request(self, request: AbstractRequest) -> AbstractResponse:
        """
        Find response by request

        @param request: Request to find response for
        @raise OkResponseNotFoundException: If response not found
        @return: Response
        """
        response_body: ExecuteV2ResponseBody = self.get_body()
        for response in response_body.responses_batch:
            if response.request == request:
                return response
        raise OkResponseNotFoundException(f'Response for request {request} not found')


class ExecuteV2Request(AbstractRequest):
    def is_json(self) -> bool:
        return False

    @property
    def http_method(self) -> OkRequestHttpMethod:
        return OkRequestHttpMethod.POST

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return ExecuteV2Response

    @property
    def method_group(self) -> str:
        return 'batch'

    @property
    def method(self) -> str:
        return 'executeV2'

    @property
    def params(self) -> PARAMS:
        return self._params

    def __init__(self, id: str):
        self.id = id
        self._params: BatchExecuteParams = BatchExecuteParams()

    def to_execute_dict(self) -> dict:
        result = self._params.to_execute_dict()
        result['id'] = self.id
        return result

    def append(self, request: AbstractRequest):
        self._params.request_storage.append(request)
