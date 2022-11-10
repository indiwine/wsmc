from .basicresponse import BasicResponse


class UserResponse(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'user'

    @property
    def first_name(self) -> str:
        return self.update['first_name']

    @property
    def last_name(self) -> str:
        return self.update['last_name']

    @property
    def username(self) -> str:
        return self.update['username']

    @property
    def account_name(self) -> str:
        username = self.first_name
        username = username.strip()
        username += self.last_name
        username = username.strip()
        nickname: str = self.username
        if len(nickname) > 0:
            username += f' ({nickname})'
        return username.strip()