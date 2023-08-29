from social_media.mimic.ok.flows.okloginflow import OkLoginFlow
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkLoginCollector(AbstractCollector[OkRequestData, OkOptions]):
    async def handle(self, request: Request[OkRequestData]):
        login_flow = OkLoginFlow(request.data.client)
        login_response = await login_flow.login(
            request.credentials.user_name,
            request.credentials.password,
            session_dto=request.credentials.session_dto
        )

        session_dto = login_response.to_session_dto()
        session_dto.cookie_jar = request.data.client.jar.to_base64()

        request.credentials.session = session_dto
        request.credentials.save()

        return super().handle(request)
