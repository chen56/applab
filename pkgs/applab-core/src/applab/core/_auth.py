from abc import ABC
from abc import abstractmethod
from typing import Type

from applab.core import BaseParamModel


class BaseCredential(BaseParamModel):
    pass

class _BaseAuthenticator(ABC):
    @property
    @abstractmethod
    def credential_type(self) -> Type[BaseCredential]:
        """
        抽象属性：子类必须覆盖此属性，并返回对应的 Credential Model 类型。
        注意：返回的是类本身 (Type)，而不是实例。
        """
        pass
    @abstractmethod
    def authenticate(self, credential: BaseCredential):
        pass

class BaseAKSKAuthenticator(_BaseAuthenticator, ABC):
    """
    AK/SK 的定义与起源:
    AK/SK 最早由 AWS（亚马逊云）定义，后被阿里云、华为云、百度智能云等主流云厂商沿用，成为**云服务 API 认证的通用术语**。
    - **AK**：AccessKey ID（访问密钥 ID），是「公钥」——可公开，仅用于标识用户/应用身份，无法单独用来调用 API；
    - **SK**：SecretKey / Secret Access Key（访问密钥私钥），是「私钥」——必须严格保密，用于对 API 请求进行签名，云厂商通过签名验证请求合法性。
    """
    pass