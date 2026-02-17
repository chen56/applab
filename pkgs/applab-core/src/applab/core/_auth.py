import datetime
from abc import ABC, abstractmethod
from typing import Annotated, Optional, Type

from pydantic import ConfigDict, Field

from ._model import AppLabBase
from ._param_model import BaseParamModel
from .error import check
from .storage import JsonStorage

_AUTH_ID_ALPHABET_ = "0123456789abcdefghijklmnopqrstuvwxyz"
_AUTH_ID_LENGTH_ = 12


def _new_auth_id_() -> str:
    from nanoid import generate

    return generate(_AUTH_ID_ALPHABET_, _AUTH_ID_LENGTH_)


class CredentialParam(BaseParamModel):
    # todo title rename to name? 'AuthInfo.title'
    title: Annotated[str, Field(title="Credential Title")] = "default"


class AuthInfo(AppLabBase):
    # todo 如果手工删除 json里的auth_id字段，load后又会自动补一个，这是要的效果吗？
    auth_id: Annotated[str, Field(init=False, default_factory=_new_auth_id_)]
    vendor: Annotated[str, Field(frozen=True)]
    title: str
    is_default: bool = False
    created_at: Annotated[
        datetime.datetime, Field(init=False, default_factory=lambda: datetime.datetime.now(datetime.UTC))
    ]

    model_config = ConfigDict(extra="allow")


class Authenticator(ABC):
    @property
    @abstractmethod
    def credential_type(self) -> Type[CredentialParam]:
        pass

    @abstractmethod
    def authenticate(self, credential_param: CredentialParam) -> AuthInfo:
        pass


# todo refactor 能否消除此类？
class AuthInfoList[T: AuthInfo](AppLabBase):
    auths: list[T] = []


class AuthRepo[T: AuthInfo]:
    def __init__(self, storage: JsonStorage[AuthInfoList[T]]):
        self._storage = storage
        # TODO private field被外部使用
        self._auths: AuthInfoList[T] = self._storage.load()

    @property
    def auths(self) -> list[T]:
        return self._auths.auths

    def add(self, auth: T):
        """Adds a new auth, ensuring it doesn't already exist."""
        check(not self.find_by_id(auth.auth_id), f"AuthInfo with id '{auth.auth_id}' already exists.")
        if not self._auths.auths:
            auth.is_default = True
        self._auths.auths.append(auth)
        self.save()

    def set_default(self, auth: T) -> None:
        """Sets a specific auth as the default."""
        check(auth in self._auths.auths, f"AuthInfo id'{auth.auth_id}' not found.")
        for acc in self._auths.auths:
            acc.is_default = acc.auth_id == auth.auth_id

        self.save()

    def remove(self, auth_id: str) -> T | None:
        """Removes an auth by its ID."""
        auth_to_remove = self.find_by_id(auth_id)
        if not auth_to_remove:
            return None

        self._auths.auths.remove(auth_to_remove)

        # If the removed auth was the default, set a new default if possible
        if auth_to_remove.is_default and self._auths.auths:
            self._auths.auths[0].is_default = True

        self.save()
        return auth_to_remove

    def find_by_id(self, auth_id: str) -> Optional[T]:
        """Finds an auth by its ID."""
        return next(
            (auth for auth in self._auths.auths if auth.auth_id == auth_id), None
        )

    def save(self):
        self._storage.save(self._auths, context={"show_secrets": True})
