import json
from abc import ABC
from collections.abc import Mapping

from ._account import Authenticator, AccountManager


class Vendor(ABC):
    def __init__(
            self,
            name: str,
            display_name: str,
            authenticator: Authenticator,
            account_manager: AccountManager,
            version: str = "0.0.1",
    ):
        # 实例属性（可变字段）
        self.name = name
        self.display_name = display_name
        self.version = version
        self.authenticator = authenticator
        self.account_manager = account_manager

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
        self._delegate: dict[str, Vendor] = {}

    def register(self, vendor: Vendor):
        """注册 Provider 类."""
        self._delegate[vendor.name] = vendor

    # Mapping 接口
    def __getitem__(self, key) -> Vendor:
        return self._delegate[key]

    def __iter__(self):
        return iter(self._delegate)

    def __len__(self):
        return len(self._delegate)


class Applab:
    def __init__(
            self,
            vendors: VendorRegister = VendorRegister(),
    ):
        self.vendors = vendors
