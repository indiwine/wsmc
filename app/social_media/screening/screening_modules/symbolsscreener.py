from .abstractscreeningmodule import AbstractScreeningModule
from .. import ScreeningModules
from ..screeningrequest import ScreeningRequest
from ...models import SmPostImage, ScreeningDetail


class SymbolsScreener(AbstractScreeningModule):
    def handle(self, screening_request: ScreeningRequest):
        post_images = SmPostImage.objects.select_related('post') \
            .filter(post__suspect=screening_request.suspect, prediction__isnull=False) \
            .iterator(1000)

        for post_image in post_images:
            screening_request.score += 1
            ScreeningDetail(
                report=screening_request.report,
                content_object=post_image,
                module=ScreeningModules.SYMBOLS,
                result={}
            ).save()

        super().handle(screening_request)
