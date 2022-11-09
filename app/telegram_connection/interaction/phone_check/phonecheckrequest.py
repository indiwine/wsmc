from __future__ import annotations

from ..abstractinteractionrequest import AbstractInteractionRequest


class PhoneCheckRequest(AbstractInteractionRequest):
    phone: str
    name: str

    def set_arguments(self, phone: str, name: str) -> PhoneCheckRequest:
        self.phone = phone
        self.name = name
        return self
