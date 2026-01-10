from applab.core._constant import _APPLAB
from applab.core._storage import JsonStorage
import json
from abc import ABC
from collections.abc import Mapping

from ._account import Authenticator, CloudAccounts


class Vendor(ABC):
    def __init__(
            self,
            name: str,
            display_name: str,
            version: str = "0.0.1",
            authenticator: Authenticator = None,
    ):
        # 实例属性（可变字段）
        self.name = name
        self.display_name = display_name
        self.version = version
        self.authenticator = authenticator

    def info(self) -> dict:
        """返回 vendor 信息字典."""
        return {
            "name": self.name,
            "version": self.version,
        }

    def __str__(self):
        return json.dumps(self.info())


class VendorRegister(Mapping[str, Vendor]):
    """只读 Provider 注册表."""

    def __init__(self):
        self._registry: dict[str, Vendor] = {}

    def register(self, vendor: Vendor):
        """注册 Provider 类."""
        self._registry[vendor.name] = vendor

    # Mapping 接口
    def __getitem__(self, key) -> Vendor:
        return self._registry[key]

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)


class Applab:
    def __init__(
            self,
            vendors: VendorRegister = VendorRegister(),
            account_storage: JsonStorage[CloudAccounts] = JsonStorage(path=_APPLAB.ACCOUNTS_FILE, model=CloudAccounts),
    ):
        self.vendors = vendors
        self.account_storage = account_storage
