from typing import Any

from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from .phonecheckrequest import PhoneCheckRequest


class GetFbPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        request.agent.send_message_contact(request.chat.id, {
            'phone_number': request.phone,
            'first_name': request.name
        })

        same_chat_predicate = self.get_same_chat_predicate(request.chat)

        messages = request.agent.wait_for_massage(same_chat_predicate, stop_predicate=same_chat_predicate)
        return self.messages_to_list(messages)
