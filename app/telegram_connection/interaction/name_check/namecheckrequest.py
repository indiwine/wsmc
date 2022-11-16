from __future__ import annotations

from ..abstractinteractionrequest import AbstractInteractionRequest


class NameCheckRequest(AbstractInteractionRequest):
    name: str

    def set_arguments(self, name: str) -> NameCheckRequest:
        self.name = name
        return self
