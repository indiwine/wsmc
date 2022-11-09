import asyncio
from asyncio import Future
from typing import TypedDict, Optional, Callable, List

from django.conf import settings
from telegram.client import Telegram, AuthorizationState
from telegram.utils import AsyncResult

from telegram_connection.models import TelegramAccount
from .responses import available_responses, ChatResponse, ChatsResponse, MessageResponse
from .responses.basicresponse import BasicResponse
from ..exceptions import NoResponseWrapperFound, ChatNotFound


class TgContactMessage(TypedDict, total=False):
    phone_number: str
    first_name: str
    last_name: Optional[str]
    vcard: Optional[str]
    user_id: Optional[int]


MessageResponseHandler = Callable[[MessageResponse], None]
MessageResponsePredicate = Callable[[MessageResponse], bool]


class TgAgent:
    _update_msg_subscribers: List[MessageResponseHandler] = []

    def __init__(self, tg_account: TelegramAccount):
        """
        Basic agent for connecting with a telegram
        @param tg_account: Account to work with
        """
        self.tg_account = tg_account
        self.tg = Telegram(
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            phone=tg_account.phone.__str__(),
            database_encryption_key=settings.TELEGRAM_DATABASE_ENCRYPTION_KEY,
            device_model='WSMC App',
            system_version='latest',
            tdlib_verbosity=2,
            use_message_database=False
        )

    def on_msg_update(self, handler: MessageResponseHandler):
        self._update_msg_subscribers.append(handler)

    def wait_for_massage(self, predicate: MessageResponsePredicate, timeout: float = 30.0):
        return asyncio.run(asyncio.wait_for(self._wait_for_msg(predicate), timeout=timeout))

    async def _wait_for_msg(self, predicate: MessageResponsePredicate) -> MessageResponse:
        future = Future()

        def handler(msg: MessageResponse):
            if predicate(msg):
                future.set_result(msg)

        self.on_msg_update(handler)

        await future

        self._update_msg_subscribers.remove(handler)
        return future.result()

    def login(self) -> AuthorizationState:
        """
        Login into telegram account
        @return:
        """
        code = self.tg.login(False)
        self.tg.add_message_handler(self._upd_msg_handler)
        return code

    def stop(self):
        """
        Stop telegram listeners and free up resources
        """
        return self.tg.stop()

    def find_chat_or_fail(self, chat_name: str) -> ChatResponse:
        """
        Find chat by its name (user must be IN this chat for to be found)

        @raise ChatNotFound if no chat with such name could be found
        @param chat_name:
        @return: found chat
        """
        self._wait(self.tg.get_chats())
        chats: ChatsResponse = self._wait_and_wrap(self.tg.call_method('searchChats', {"query": chat_name, 'limit': 1}))
        if chats.total == 0:
            raise ChatNotFound(f'Cannot find chat: "{chat_name}"')
        return self.get_chat(chats.first_chat_id)

    def send_message_contact(self, chat_id: int, contact: TgContactMessage):
        data = {
            'chat_id': chat_id,
            'input_message_content': {
                '@type': 'inputMessageContact',
                'contact': {
                    '@type': 'contact',
                    **contact
                }
            }
        }
        return self.tg.call_method('sendMessage', data, False)

    def get_chat(self, id: int) -> ChatResponse:
        return self._wait_and_wrap(self.tg.get_chat(id))

    def _upd_msg_handler(self, update: dict):
        result = AsyncResult(self.tg)
        result.parse_update(update['message'])
        wrapped_msg = MessageResponse(result)
        for cl in self._update_msg_subscribers:
            cl(wrapped_msg)

    @staticmethod
    def _wait_and_wrap(async_result: AsyncResult) -> BasicResponse:
        """
        Wait for result and wrap the response into basic response

        @param async_result:
        @return: Wrapped response
        """
        TgAgent._wait(async_result)
        for wrapper in available_responses:
            if wrapper.define_applicable_type() == async_result.update['@type']:
                return wrapper(async_result)
        raise NoResponseWrapperFound(
            f"Cannot find appropriate response wrapper for @type: `{async_result.update['@type']}`")

    @staticmethod
    def _wait(async_result: AsyncResult):
        """
        Wait for telegram to process request

        @raise RuntimeError if something went wrong
        @param async_result:
        """
        async_result.wait(raise_exc=True)
