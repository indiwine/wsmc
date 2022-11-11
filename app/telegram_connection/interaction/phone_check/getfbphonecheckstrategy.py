from typing import Any

from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from .phonecheckrequest import PhoneCheckRequest


class GetFbPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        request.agent.send_message_contact(request.chat.id, {
            'phone_number': request.phone,
            'first_name': request.name
        })

        predicate = lambda update_msg: not update_msg.is_outgoing and update_msg.chat_id == request.chat.id

        messages = request.agent.wait_for_massage(predicate, stop_predicate=predicate)
        return self.join_messages(messages)
