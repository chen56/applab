import datetime
from abc import ABC, abstractmethod
from typing import Annotated, Optional, Type

from pydantic import ConfigDict, Field

from ._model import AppLabBase
from ._param_model import BaseParamModel
from .error import check
from .storage import JsonStorage

_ACCOUNT_ID_ALPHABET_ = "0123456789abcdefghijklmnopqrstuvwxyz"
_ACCOUNT_ID_LENGTH_ = 12


def _new_account_id_() -> str:
    from nanoid import generate

    return generate(_ACCOUNT_ID_ALPHABET_, _ACCOUNT_ID_LENGTH_)


class CredentialParam(BaseParamModel):
    # todo title rename to name? 'Account.title'
    title: Annotated[str, Field(title="Credential Title")] = "default"


class Account(AppLabBase):
    # todo 如果手工删除 json里的account_id字段，load后又会自动补一个，这是要的效果吗？
    account_id: Annotated[str, Field(init=False, default_factory=_new_account_id_)]
    vendor: str
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
    def authenticate(self, credential_param: CredentialParam) -> Account:
        pass

# todo refactor 能否消除此类？
class AccountList[T: Account](AppLabBase):
    accounts: list[T] = []


class AccountManager[T: Account]:
    def __init__(self, storage: JsonStorage[AccountList[T]]):
        self._storage = storage
        self._accounts: AccountList[T] = self._storage.load()

    @property
    def accounts(self) -> list[T]:
        return self._accounts.accounts

    def add(self, account: T):
        """Adds a new account, ensuring it doesn't already exist."""
        check(not self.find_by_id(account.account_id), f"Account with id '{account.account_id}' already exists.")
        if not self._accounts.accounts:
            account.is_default = True
        self._accounts.accounts.append(account)
        self.save()

    def set_default(self, account: T) -> None:
        """Sets a specific account as the default."""
        check(account in self._accounts.accounts, f"Account id'{account.account_id}' not found.")
        for acc in self._accounts.accounts:
            acc.is_default = acc.account_id == account.account_id

        self.save()

    def remove(self, account_id: str) -> T | None:
        """Removes an account by its ID."""
        account_to_remove = self.find_by_id(account_id)
        if not account_to_remove:
            return None

        self._accounts.accounts.remove(account_to_remove)

        # If the removed account was the default, set a new default if possible
        if account_to_remove.is_default and self._accounts.accounts:
            self._accounts.accounts[0].is_default = True

        self.save()
        return account_to_remove

    def find_by_id(self, account_id: str) -> Optional[T]:
        """Finds an account by its ID."""
        return next(
            (account for account in self._accounts.accounts if account.account_id == account_id), None
        )

    def save(self):
        self._storage.save(self._accounts, context={"show_secrets": True})
