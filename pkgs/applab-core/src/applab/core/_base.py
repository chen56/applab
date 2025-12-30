import json
from abc import ABC, abstractmethod
from collections.abc import Mapping


class ProviderBase:
    def __init__(self, name: str, version: str = "0.0.1"):
        # 实例属性（可变字段）
        self.name = name
        self.version = version

    def info(self) -> dict:
        """返回 provider 信息字典."""
        return {
            "name": self.name,
            "version": self.version,
        }

    def __str__(self):
        json.dumps(self.info())


class ProviderRegister(Mapping):
    """只读 Provider 注册表."""

    def __init__(self):
        self._registry: dict[str, type[ProviderBase]] = {}
        self._registry2: dict[str, ProviderBase] = {}

    def register(self, provider_cls: type[ProviderBase]):
        """注册 Provider 类."""
        self._registry[provider_cls.name] = provider_cls

    # Mapping 接口
    def __getitem__(self, key):
        return self._registry[key]

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)
