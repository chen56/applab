from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Type, Optional, Annotated

from pydantic import BaseModel, Field

from ._param_model import BaseParamModel


import json
import base64
from pathlib import Path


class CredentialParam(BaseParamModel):
    name:Annotated[str, Field(title="Name", description="Credential name")] = "default"

class CloudAccount(BaseModel):
    name: str
    vendor: str
    verified: bool = False
    verified_at: Optional[datetime] = None

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


class CloudAccountManager:
    def __init__(self):
        self.config_dir = Path.home() / ".applab"
        self.config_path = self.config_dir / "accounts.json"
        self._ensure_config_exists()
        self.current_account = None

    def _ensure_config_exists(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        if not self.config_path.exists():
            with open(self.config_path, 'w') as f:
                json.dump({"accounts": {}}, f)

    def encrypt_key(self, key: str) -> str:
        # 实际生产环境建议使用 cryptography 库，此处演示基础混淆
        return base64.b64encode(key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        return base64.b64decode(encrypted_key.encode()).decode()

    def save_account(self, account:CloudAccount):
        """保存 Account 信息"""
        with open(self.config_path, 'r') as f:
            data = json.load(f)

        data.setdefault("accounts", {}).setdefault(account.vendor, {})[account.name]=account.model_dump(mode="json",exclude_unset=True)
        print("------",data)
        print("------",account.model_dump(mode="json",exclude_unset=True))
        print("------",account.model_dump_json(indent=4))
        with open(self.config_path, 'w') as f:
            s=json.dumps(data,indent=4)
            f.write(s)
        return True

    def get_account(self, account_name):
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        return data["accounts"].get(account_name)

