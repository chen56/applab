import datetime
from abc import ABC
from abc import abstractmethod
from typing import Type, Annotated

from pydantic import BaseModel, Field, model_validator

from ._constant import APPLAB
from ._param_model import BaseParamModel

_ACCOUNT_ID_ALPHABET_ = "0123456789abcdefghijklmnopqrstuvwxyz"
_ACCOUNT_ID_LENGTH_ = 12


def _new_account_id_() -> str:
    from nanoid import generate
    return generate(_ACCOUNT_ID_ALPHABET_, _ACCOUNT_ID_LENGTH_)


def _keyring_key_(account_id: str) -> str:
    return f"{APPLAB.APP_NAME}.account.{account_id}"


class CredentialParam(BaseParamModel):
    name: Annotated[str, Field(title="Name", description="Credential name")] = "default"


class CloudAccount(BaseModel):
    id: Annotated[str, Field(default_factory=_new_account_id_)]
    vendor: str
    name: str
    is_default: bool = False
    created_at: Annotated[datetime.datetime, Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))]

    @property
    def credential_key(self) -> str:
        return _keyring_key_(self.id)


class Authenticator(ABC):
    @property
    @abstractmethod
    def credential_type(self) -> Type[CredentialParam]:
        """
        抽象属性：子类必须覆盖此属性，并返回对应的 Credential Model 类型。
        注意：返回的是类本身 (Type)，而不是实例。
        """
        pass

    @abstractmethod
    def authenticate(self, credential_param: CredentialParam) -> CloudAccount:
        pass


class CloudAccounts(BaseModel):
    accounts: list[CloudAccount] = []

    # ---------- invariants ----------
    @model_validator(mode="after")
    def validate_invariants(self) -> "CloudAccounts":
        seen: set[tuple[str, str]] = set()
        default_by_vendor: dict[str, str] = {}

        for acc in self.accounts:
            key = (acc.vendor, acc.name)
            if key in seen:
                raise ValueError(f"Duplicate account: {acc.vendor}:{acc.name}")
            seen.add(key)

            if acc.is_default:
                if acc.vendor in default_by_vendor:
                    raise ValueError(
                        f"Multiple default accounts for vendor={acc.vendor}"
                    )
                default_by_vendor[acc.vendor] = acc.id

        return self

    def add(self, account: CloudAccount) -> CloudAccount:
        """
        Add a CloudAccount to CloudAccounts.

        Rules:
        - The account.name is auto-generated if missing.
        - Duplicate (vendor, name) for auto-generated names indicates an internal bug.
        - set_default=True marks this account as the default for its vendor.
        """
        # ---------- 1. assign name if missing ----------
        if not account.name:
            account.name = self.generate_name(account.vendor)

        # ---------- 2. internal invariant check ----------
        if any(a.vendor == account.vendor and a.name == account.name for a in self.accounts):
            # 自动生成的 name 出现重复 → 程序 bug
            raise RuntimeError(
                f"Duplicate account generated internally (BUG): {account.vendor}:{account.name}"
            )

        # ---------- 5. append ----------
        self.accounts.append(account)
        return account

    # ---------- helpers ----------
    def find(self, vendor: str, name: str | None = None) -> CloudAccount:
        if name:
            for acc in self.accounts:
                if acc.vendor == vendor and acc.name == name:
                    return acc
            raise KeyError(f"Account not found: {vendor}:{name}")

        # no name → use default
        defaults = [a for a in self.accounts if a.vendor == vendor and a.is_default]
        if defaults:
            return defaults[0]

        raise KeyError(f"No default account for vendor={vendor}")

    def existing_names(self, vendor: str) -> set[str]:
        return {a.name for a in self.accounts if a.vendor == vendor}

    def generate_name(self, vendor: str) -> str:
        names = self.existing_names(vendor)
        if "default" not in names:
            return "default"
        i = 2
        while f"default-{i}" in names:
            i += 1
        return f"default-{i}"

    def set_default(self, account: CloudAccount):
        for acc in self.accounts:
            if acc.vendor == account.vendor:
                acc.is_default = False
        account.is_default = True
