import asyncio
import logging
import time
from pprint import pprint
from typing import TypedDict, Optional, Callable, List, Union

from django.conf import settings
from telegram.client import Telegram, AuthorizationState
from telegram.utils import AsyncResult

from telegram_connection.models import TelegramAccount
from .responses import available_responses, ChatResponse, ChatsResponse, MessageResponse, UserResponse, \
    CallbackQueryAnswer
from .responses.basicresponse import BasicResponse
from ..exceptions import NoResponseWrapperFound, ChatNotFound, AccountNotLoggedIn

logger = logging.getLogger(__name__)


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
            use_message_database=False,
            use_test_dc=False
        )

    def wait_for_massage(self,
                         collect_predicate: MessageResponsePredicate,
                         timeout: float = 30.0,
                         stop_predicate: Optional[MessageResponsePredicate] = None) -> List[MessageResponse]:
        f"""
        A synchronous version of await_for_message
        @param collect_predicate:
        @param timeout:
        @param stop_predicate:
        @return:
        """
        return asyncio.run(self.await_for_message(collect_predicate, timeout, stop_predicate))

    def on_msg_update(self, handler: MessageResponseHandler):
        self._update_msg_subscribers.append(handler)

    # @staticmethod
    # def up():
    #     r = TelegramAccount.objects.get(id=14)
    #     agent = TgAgent(r)
    #     agent.login_or_fail()
    #     agent.refresh_chats()
    #     chat = agent.find_chat_or_fail('Quick OSINT')
    #     agent.send_message_text(chat.id, '+79876543210')
    #
    #     # agent.send_message_contact(chat.id, {'phone_number': '+79876543210', 'first_name': 'Мдлодло'})
    #
    #     def collect_predicate(msg: MessageResponse):
    #         return msg.chat_id == chat.id and not msg.is_outgoing
    #
    #     def stop_predicate(msg: MessageResponse):
    #         if collect_predicate(msg):
    #             if msg.has_message_text:
    #                 return '@Qu1ck_os11nt_bot' in msg.content.get_text
    #             if msg.has_reply_markup:
    #                 return msg.reply_markup.has_btn_with_text('Дополнительные методы поиска')
    #         return False
    #
    #     # def stop(msg: MessageResponse):
    #     #     end_msgs = [
    #     #         '@Qu1ck_os11nt_bot'
    #     #     ]
    #     #     return collect_predicate(msg) and any(
    #     #         test_str in msg.message_text.palin_text for test_str in end_msgs)
    #
    #     return (agent.wait_for_massage(collect_predicate, timeout=60.0, stop_predicate=stop_predicate), agent)

    def get_me(self) -> UserResponse:
        return self._wait_and_wrap(self.tg.get_me())

    async def await_for_message(self,
                                collect_predicate: MessageResponsePredicate,
                                timeout: float = 30.0,
                                stop_predicate: Optional[MessageResponsePredicate] = None) -> List[MessageResponse]:
        """
        Collects messages from telegram
        @param collect_predicate: A callback to determine which messages should be collected
        @param timeout: timeout since last message (or start of waiting if no messages been recived)
        @param stop_predicate: A callback to determine when to stop collecting messages
        @return: List of collected messages
        """

        logger.debug('Asynchronously waiting for message')
        # Get the current event loop.
        loop = asyncio.get_running_loop()

        # Create a new Future object.
        future = loop.create_future()

        msg_collection = []

        last_msg = time.monotonic()

        def resolve():
            loop.call_soon_threadsafe(future.set_result, msg_collection)

        def handler(msg: MessageResponse):
            if collect_predicate(msg):
                nonlocal last_msg
                last_msg = time.monotonic()
                logger.debug(f'Collecting message')
                pprint(msg.update)
                msg_collection.append(msg)

            if stop_predicate is not None and stop_predicate(msg):
                logger.debug(f'Awaited message found')
                pprint(msg.update)
                resolve()

        async def wait_for_last():
            while True:
                logger.debug(f"last msg: {last_msg}")
                if future.done():
                    return
                if last_msg + timeout < time.monotonic():
                    logger.debug('Timeout from last message reached')
                    resolve()
                    return
                else:
                    await asyncio.sleep(1)

        self.on_msg_update(handler)
        await asyncio.gather(future, wait_for_last())
        logger.debug(f'Future resolved')
        self._update_msg_subscribers.remove(handler)
        return future.result()

    def login(self) -> AuthorizationState:
        """
        Login into telegram account
        @return:
        """
        logger.debug(f'Trying to log in {self.tg_account.__str__()}')
        code = self.tg.login(False)
        logger.info(f'TG Login status code: {code}')
        self.tg.add_message_handler(self._upd_msg_handler)
        return code

    def logout(self):
        return self._wait(self.tg.call_method('logOut', block=False))

    def login_or_fail(self) -> None:
        """
        Login into tg account. Fails if status is not ready.
        """
        code = self.login()
        if code != AuthorizationState.READY:
            raise AccountNotLoggedIn(self.tg_account)

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
        logger.debug(f'Looking for chat: "{chat_name}"')
        chats: ChatsResponse = self._wait_and_wrap(self.tg.call_method('searchChats', {"query": chat_name, 'limit': 1}))
        if chats.total == 0:
            raise ChatNotFound(f'Cannot find chat: "{chat_name}"')
        return self.get_chat(chats.first_chat_id)

    def refresh_chats(self):
        self._wait(self.tg.get_chats())

    def open_and_mark_read(self, chat: ChatResponse, msgs: List[MessageResponse]):
        chat_data = {'chat_id': chat.id}
        self._wait(self.tg.call_method('openChat', chat_data, False))
        view_data = {
            'chat_id': chat.id,
            'message_thread_id': 0,
            'message_ids': list(map(lambda msg: msg.id, msgs))
        }
        self._wait(self.tg.call_method('viewMessages', view_data, False))
        self._wait(self.tg.call_method('closeChat', chat_data, False))

    def get_callback_query_answer(self, msg: MessageResponse, callback_data: str) -> CallbackQueryAnswer:
        """
        Send a callback query to a bot

        Typically, this is a way to trigger a bot button press
        @param msg:
        @param callback_data:
        @return:
        """
        data = {
            'chat_id': msg.chat_id,
            'message_id': msg.id,
            'payload': {
                '@type': 'callbackQueryPayloadData',
                'data': callback_data
            }
        }
        return self._wait_and_wrap(self.tg.call_method('getCallbackQueryAnswer', data, False))

    def send_message_contact(self, chat_id: int, contact: TgContactMessage) -> MessageResponse:
        """
        Send "contact" message
        @param chat_id:
        @param contact:
        @return:
        """
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
        return self._wait_and_wrap(self.tg.call_method('sendMessage', data, False))

    def send_message_text(self, chat_id: Union[int, ChatResponse], msg: str) -> MessageResponse:
        return self._wait_and_wrap(self.tg.send_message(self._extract_chat_id(chat_id), msg))

    def get_chat(self, id: int) -> ChatResponse:
        return self._wait_and_wrap(self.tg.get_chat(id))

    def _upd_msg_handler(self, update: dict):
        result = AsyncResult(self.tg)
        result.parse_update(update['message'])
        wrapped_msg = MessageResponse(result)
        for cl in self._update_msg_subscribers:
            cl(wrapped_msg)

    @staticmethod
    def _extract_chat_id(chat_id: Union[int, ChatResponse]) -> int:
        if isinstance(chat_id, ChatResponse):
            return chat_id.id
        return chat_id

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
