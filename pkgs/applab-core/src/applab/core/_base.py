import json
from collections.abc import Mapping


class VendorBase:
    def __init__(self, name: str, version: str = "0.0.1"):
        # 实例属性（可变字段）
        self.name = name
        self.version = version

    def info(self) -> dict:
        """返回 vendor 信息字典."""
        return {
            "name": self.name,
            "version": self.version,
        }

    def __str__(self):
        return json.dumps(self.info())


class ProviderRegister(Mapping):
    """只读 Provider 注册表."""

    def __init__(self):
        self._registry: dict[str, VendorBase] = {}

    def register(self, vendor: VendorBase):
        """注册 Provider 类."""
        self._registry[vendor.name] = vendor

    # Mapping 接口
    def __getitem__(self, key):
        return self._registry[key]

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)


class Applab:
    def __init__(self):
        self.runtimes = ProviderRegister()


applab = Applab()
