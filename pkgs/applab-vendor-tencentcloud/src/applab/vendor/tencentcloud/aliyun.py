from typing import Annotated, Type

from pydantic import SecretStr, Field

from applab.core import CredentialParam
from applab.core import Vendor
from applab.core import Authenticator


# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================


class AliyunAKSKCredentialParam(CredentialParam):
    access_key_id: Annotated[str, Field(title="AccessKey ID", description="Aliyun Cloud API AccessKey ID")]
    access_key_secret: Annotated[
        SecretStr, Field(title="AccessKey Secret", description="Aliyun Cloud API AccessKey Secret")
    ]


class AliyunAKSKAuthenticator(Authenticator):
    @property
    def credential_type(self) -> Type[AliyunAKSKCredentialParam]:
        return AliyunAKSKCredentialParam

    def authenticate(self, credential: AliyunAKSKCredentialParam):
        pass


class AliyunVendor(Vendor):
    def __init__(self, version: str):
        super().__init__(
            name="aliyun",
            display_name="阿里云",
            version=version,
            authenticator=AliyunAKSKAuthenticator(),
        )
