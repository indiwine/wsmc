from __future__ import annotations

import dataclasses
import time
from abc import ABC, abstractmethod
from typing import List

from social_media.mimic.ok.log_requests.reader import OkLogStreamDecoder, BurpSuiteRequestsReader
from social_media.mimic.ok.requests.log.externallog import ExternalLogRequest, ExternalLogItem, ExternalLogData, \
    ExternalLogParams


class AbstractLogRequestMockFilter(ABC):
    @abstractmethod
    def __call__(self, task: LogRequestMockTask) -> LogRequestMockTask:
        raise NotImplementedError


class LoadBurpSuiteRequestsFilter(AbstractLogRequestMockFilter):
    def __call__(self, task: LogRequestMockTask) -> LogRequestMockTask:
        task.raw_requests = list(OkLogStreamDecoder(BurpSuiteRequestsReader()).decode(task.file_path))
        return task


class ConvertToLogRequestFilter(AbstractLogRequestMockFilter):
    def __call__(self, task: LogRequestMockTask) -> LogRequestMockTask:
        task.log_requests = []
        for raw_request in task.raw_requests:
            task.log_requests.append(self.build_log_request(raw_request))
        return task

    @staticmethod
    def build_log_items(raw_log_items: List[dict]) -> List[ExternalLogItem]:
        return [ExternalLogItem(**raw_log_item) for raw_log_item in raw_log_items]

    @staticmethod
    def build_log_data(log_items: List[ExternalLogItem]) -> ExternalLogData:
        return ExternalLogData(items=log_items)

    @classmethod
    def build_log_request(cls, raw_request: dict) -> ExternalLogRequest:
        if 'data' in raw_request and 'items' in raw_request['data']:
            log_items = cls.build_log_items(raw_request['data']['items'])
            log_data = cls.build_log_data(log_items)
            log_params = ExternalLogParams(data=log_data, collector=raw_request['collector'])
            return ExternalLogRequest(log_params)
        else:
            raise RuntimeError(f'Invalid request: {raw_request}')


class UpdateTimestampsFilter(AbstractLogRequestMockFilter):
    def __call__(self, task: LogRequestMockTask) -> LogRequestMockTask:
        base_timestamp = round(time.time() * 1000)

        for log_request in task.log_requests:
            # Update timestamps of log items to be relative to base_timestamp
            # for each next request we use timestamp of the last item of the previous request
            base_timestamp = log_request.update_timestamps_relative(base_timestamp)

        return task


@dataclasses.dataclass
class LogRequestMockTask:
    file_path: str
    raw_requests: List[dict] = None
    log_requests: List[ExternalLogRequest] = None


class LogRequestMockPipeline:
    def __init__(self):
        self._filters: List[AbstractLogRequestMockFilter] = []

    def pipe(self, *filters: AbstractLogRequestMockFilter) -> LogRequestMockPipeline:
        self._filters = self._filters + list(filters)
        return self

    def execute(self, task: LogRequestMockTask) -> LogRequestMockTask:
        for pipe_filter in self._filters:
            task = pipe_filter(task)
        return task

    @classmethod
    def build(cls, *filters: AbstractLogRequestMockFilter) -> LogRequestMockPipeline:
        pipeline = cls()
        pipeline.pipe(*filters)
        return pipeline

    @staticmethod
    def default_filters() -> List[AbstractLogRequestMockFilter]:
        return [
            LoadBurpSuiteRequestsFilter(),
            ConvertToLogRequestFilter(),
            UpdateTimestampsFilter()
        ]

    @classmethod
    def execute_task(cls, task: LogRequestMockTask) -> LogRequestMockTask:
        pipeline = LogRequestMockPipeline.build(*cls.default_filters())
        return pipeline.execute(task)
