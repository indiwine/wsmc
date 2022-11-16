from __future__ import annotations

from ..abstractinteractionrequest import AbstractInteractionRequest


class EmailCheckRequest(AbstractInteractionRequest):
    email: str

    def set_arguments(self, email: str) -> EmailCheckRequest:
        self.email = email
        return self
