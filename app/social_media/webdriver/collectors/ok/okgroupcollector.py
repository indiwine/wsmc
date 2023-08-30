from social_media.mimic.ok.flows.okgroupflow import OkGroupFlow
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkGroupCollector(AbstractCollector[OkRequestData, OkOptions]):
    async def handle(self, request: Request[OkRequestData]):
        group_flow = OkGroupFlow(request.data.client)
        group_uid = await group_flow.resolve_group_uid(request.target_url)
        group_info = await group_flow.fetch_group_info(group_uid)
        group_dtp = group_info.to_group_dto()
        await self.apersist_group(group_dtp, request, request.suspect_identity)
