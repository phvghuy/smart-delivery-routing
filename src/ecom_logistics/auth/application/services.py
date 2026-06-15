from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthToken:
    access_token: str
    role: str


class AuthService(ABC):
    @abstractmethod
    def sign_in(self, email: str, password: str) -> AuthToken: ...

    @abstractmethod
    def sign_out(self, token: str) -> None: ...

    @abstractmethod
    def get_user_role(self, access_token: str) -> str | None: ...

    @abstractmethod
    def get_user_id(self, access_token: str) -> str: ...