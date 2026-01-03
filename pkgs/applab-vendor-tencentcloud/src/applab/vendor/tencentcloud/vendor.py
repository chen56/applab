from typing import Annotated

from pydantic import Field
from pydantic.types import SecretStr

from applab.core import BaseAKSKAuthenticator, BaseCredentialModel
from applab.core import BaseVendor


# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================
class TencentCloudVendor(BaseVendor):

    def __init__(self, name: str, version: str):
        super().__init__(
            name=name,
            version=version,
            aksk_authenticator=TencentCloudAuthenticator(),
        )


class TencentCloudCredential(BaseCredentialModel):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAuthenticator(BaseAKSKAuthenticator):
    def authenticate(self, credential: TencentCloudCredential):
        pass
