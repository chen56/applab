import datetime
from abc import ABC, abstractmethod
from typing import Type, Annotated, List

from pydantic import BaseModel, Field, ConfigDict

from ._constant import APPLAB
from ._param_model import BaseParamModel
from .storage import JsonStorage

_ACCOUNT_ID_ALPHABET_ = "0123456789abcdefghijklmnopqrstuvwxyz"
_ACCOUNT_ID_LENGTH_ = 12


def _new_account_id_() -> str:
    from nanoid import generate

    return generate(_ACCOUNT_ID_ALPHABET_, _ACCOUNT_ID_LENGTH_)


def _keyring_key_(account_id: str) -> str:
    return f"{APPLAB.APP_NAME}.account.{account_id}"


class CredentialParam(BaseParamModel):
    title: Annotated[str, Field(title="Credential Title")] = "default"


class Account(BaseModel):
    id: Annotated[str, Field(init=False, default_factory=_new_account_id_)]
    vendor: str
    title: str
    is_default: bool = False
    created_at: Annotated[
        datetime.datetime, Field(init=False, default_factory=lambda: datetime.datetime.now(datetime.UTC))
    ]

    model_config = ConfigDict(extra="allow")

    @property
    def credential_key(self) -> str:
        return _keyring_key_(self.id)


class Authenticator(ABC):
    @property
    @abstractmethod
    def credential_type(self) -> Type[CredentialParam]:
        pass

    @abstractmethod
    def authenticate(self, credential_param: CredentialParam) -> Account:
        pass


class AccountList[T:Account](BaseModel):
    accounts: List[T] = []


class AccountManager[T:Account]:
    def __init__(self, storage: JsonStorage[AccountList[T]]):
        self.storage = storage
        self.accounts: AccountList[T] = self.storage.load()

    def add(self, account: T):
        self.accounts.accounts.append(account)
        self.save()

    def set_default(self, account: T):
        for acc in self.accounts.accounts:
            acc.is_default = False
        account.is_default = True
        self.save()

    def save(self):
        self.storage.save(self.accounts)
