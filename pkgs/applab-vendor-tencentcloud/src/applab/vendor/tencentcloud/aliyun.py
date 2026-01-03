from typing import Annotated

from pydantic import SecretStr, Field

from applab.core import BaseAKSKAuthenticator, BaseCredentialModel
from applab.core import BaseVendor


# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================

class AliyunAKSKCredential(BaseCredentialModel):
    access_key_id: Annotated[str, Field(title="AccessKey ID", description="Aliyun Cloud API AccessKey ID")]
    access_key_secret: Annotated[
        SecretStr, Field(title="AccessKey Secret", description="Aliyun Cloud API AccessKey Secret")]


class AliyunAKSKAuthenticator(BaseAKSKAuthenticator):
    def authenticate(self, credential: AliyunAKSKCredential):
        pass


class AliyunVendor(BaseVendor):

    def __init__(self, name: str, version: str):
        super().__init__(
            name=name,
            version=version,
            aksk_authenticator=AliyunAKSKAuthenticator(),
        )
