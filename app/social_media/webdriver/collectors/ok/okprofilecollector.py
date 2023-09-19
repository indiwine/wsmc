from social_media.mimic.ok.flows.okcommonflow import OkCommonFlow
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkProfileCollector(AbstractCollector[OkRequestData, OkOptions]):
    async def handle(self, request: Request[OkRequestData]):
        common_flow = OkCommonFlow(request.data.client)
        user_id = await common_flow.resolve_url_to_uid(request.target_url)
        request.data.user_id = user_id
        user_info = await common_flow.fetch_user_info(user_id)
        user_profile, _ = await self.apersist_sm_profile(user_info.to_profile_dto(), request)
        request.data.profile_model = user_profile
