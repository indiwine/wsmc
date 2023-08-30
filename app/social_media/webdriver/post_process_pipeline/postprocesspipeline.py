from __future__ import annotations

from typing import List

from .filters.basepostprocessfilter import BasePostProcessFilter
from .postprocesstask import PostProcessTask
from ..pipe.abstractasyncpipeline import AbstractAsyncPipeline


class PostProcessPipeline(AbstractAsyncPipeline[BasePostProcessFilter, PostProcessTask]):
    """
    Pipeline for post-processing
    """
