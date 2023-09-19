from abc import ABC, abstractmethod

from ..postprocesstask import PostProcessTask


class BasePostProcessFilter(ABC):
    @abstractmethod
    async def __call__(self, task: PostProcessTask) -> PostProcessTask:
        pass
