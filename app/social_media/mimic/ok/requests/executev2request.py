from typing import List, Union

from .abstractrequest import AbstractRequest, PARAMS, AbstractRequestParams


class BatchExecuteParams(AbstractRequestParams):
    request_storage: List[AbstractRequest] = []

    def to_execute_dict(self) -> dict:
        result = []

        for req in self.request_storage:
            result.append({
                req.dotted_method_name: {
                    "params": req.params.to_execute_dict()
                }
            })

        return result


class ExecuteV2Request(AbstractRequest):
    @property
    def method_group(self) -> str:
        return 'batch'

    @property
    def method(self) -> str:
        return 'executeV2'

    @property
    def params(self) -> PARAMS:
        return self._params

    def __init__(self):
        self._params: BatchExecuteParams = BatchExecuteParams()

    def to_execute_dict(self) -> dict:
        pass

    def append(self, request: AbstractRequest):
        self._params.request_storage.append(request)
