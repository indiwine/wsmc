import logging
from dataclasses import asdict

from social_media.mimic.ok.flows.okloginflow import OkLoginFlow
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)
class OkLoginCollector(AbstractCollector[OkRequestData, OkOptions]):
    async def handle(self, request: Request[OkRequestData]):
        """
        Perform login
        @param request:
        @return:
        """
        login_flow = OkLoginFlow(request.data.client)
        if self.get_options().use_login_jitter:
            logger.info('Using login jitter')
            await self.random_await(10, 60)

        login_response = await login_flow.login(
            request.credentials.user_name,
            request.credentials.password,
            session_dto=request.credentials.session_dto
        )

        session_dto = login_response.to_session_dto()
        session_dto.cookie_jar = request.data.client.jar.to_base64()
        session_dto.android_device = request.data.client.device

        request.credentials.session = asdict(session_dto)
        await request.credentials.asave()

