from abc import ABC, abstractmethod

from typing import Generic, TypeVar

TASK_TYPE = TypeVar('TASK_TYPE')


class AbstractPipeFilter(ABC, Generic[TASK_TYPE]):
    """
    Abstract class for async pipeline filters
    """

    @abstractmethod
    async def __call__(self, task: TASK_TYPE) -> TASK_TYPE:
        pass


FILTER_TYPE = TypeVar('FILTER_TYPE', bound=AbstractPipeFilter)


class AbstractAsyncPipeline(ABC, Generic[FILTER_TYPE, TASK_TYPE]):
    """
    Abstract class for async pipelines
    """
    _filters: list[FILTER_TYPE]

    async def execute(self, task: TASK_TYPE) -> TASK_TYPE:
        """
        Execute pipeline
        @param task:
        @return:
        """

        task_to_do = task
        for pipe_filter in self._filters:
            task_to_do = await pipe_filter(task_to_do)

        return task_to_do

    def pipe(self, *filters: FILTER_TYPE):
        """
        Add filters to pipeline
        @param filters:
        @return:
        """

        if not hasattr(self, '_filters'):
            self._filters = []

        self._filters = self._filters + list(filters)
        return self
