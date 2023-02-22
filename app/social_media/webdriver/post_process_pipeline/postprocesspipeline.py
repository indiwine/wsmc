from __future__ import annotations

from typing import List

from .filters.basepostprocessfilter import BasePostProcessFilter
from .postprocesstask import PostProcessTask


class PostProcessPipeline:
    def __init__(self):
        self._filters: List[BasePostProcessFilter] = []

    def pipe(self, *filters: BasePostProcessFilter) -> PostProcessPipeline:
        self._filters = self._filters + list(filters)
        return self

    async def execute(self, task: PostProcessTask):
        task_to_do = task
        for post_process_filter in self._filters:
            task_to_do = await post_process_filter(task_to_do)

        return task_to_do
