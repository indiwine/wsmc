import logging
from typing import Optional

from social_media.dtos.oksessiondto import OkSessionDto
from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.auth.anonymlogin import AnonymLoginRequest, AnonymLoginResponseBody
from social_media.mimic.ok.requests.auth.login import LoginResponseBody, LoginRequest, LoginResponse
from social_media.mimic.ok.requests.auth.loginbytoken import LoginByTokenRequest

logger = logging.getLogger(__name__)

BEFORE_LOGIN_REQUESTS_FILE_NAME = 'before_login_requests.xml'
AFTER_LOGIN_BY_TOKEN_REQUESTS_FILE_NAME = 'after_login_by_token.xml'


class OkLoginFlow(AbstractOkFlow):
    """
    Login flow for OK
    """

    async def login(self, username: str, password: str,
                    session_dto: Optional[OkSessionDto] = None) -> LoginResponseBody:
        """
        Login procedure for OK

        This method is a wrapper for full login procedure and login by token procedure
        @param username:
        @param password:
        @param session_dto:
        @return:
        """

        # Restoring cookies from session dto
        if session_dto and session_dto.cookie_jar:
            self.client.jar.from_base64(session_dto.cookie_jar)

        # If we have session dto, we can try to login by token
        if session_dto and session_dto.auth_token:
            return await self.login_by_token(session_dto.auth_token)
        # Otherwise, we need to perform full login procedure
        return await self.full_login_procedure(username, password)

    async def full_login_procedure(self, username: str, password: str) -> LoginResponseBody:
        """
        Perform full login procedure for OK

        This is a simulation of a real user login procedure for the first time.
        Modifies client session key
        @param password:
        @param username:
        @return: Login response body which can be used
        """

        logger.info(f'Performing full login procedure for {username}')

        # First we need to log in anonymously to get session key
        await self.anonymous_login()

        # Now we need to simulate log requests before login
        await self.run_requests_from_a_file(BEFORE_LOGIN_REQUESTS_FILE_NAME)

        # Now let's prepare batch request with login request
        login_request = LoginRequest(username, password)
        self.client.auth_options.screen = 'feed_main,profile_self'

        loging_response: LoginResponse = await self.perform_batch_request('auth.login', login_request)
        login_response_body: LoginResponseBody = loging_response.get_body()

        # Once we received a real session key, we need to set it to client
        self.client.set_session_key(login_response_body.session_key)
        self.client.set_current_login_data(login_response_body)

        logger.info(f'Login procedure for {username} has been completed')
        return login_response_body

    async def login_by_token(self, auth_token: str) -> LoginResponseBody:
        """
        Login by token

        Performs login by auth token procedure for OK, previously obtained from login response body
        @param auth_token:
        @return:
        """

        login_by_token_request = LoginByTokenRequest(auth_token)
        login_by_token_response: LoginResponse = await self.client.make(login_by_token_request)
        login_body = login_by_token_response.get_body()
        self.client.set_session_key(login_body.session_key)
        self.client.set_current_login_data(login_body)

        await self.run_requests_from_a_file(AFTER_LOGIN_BY_TOKEN_REQUESTS_FILE_NAME)

        return login_body

    async def anonymous_login(self) -> AnonymLoginResponseBody:
        """
        Perform anonymous login procedure for OK

        Typically, done once before first login into the app
        @return:
        """
        logger.info(f'Performing anonymous login procedure')
        anon_login_request = AnonymLoginRequest()
        anon_login_response = await self.client.make(anon_login_request)
        response_body: AnonymLoginResponseBody = anon_login_response.get_body()

        logger.debug(f'Anonym login response body: {response_body}')
        self.client.set_session_key(response_body.session_key)
        return response_body
