from typing import Annotated, Type

from pydantic import Field
from pydantic.types import SecretStr

from applab.core import BaseAKSKAuthenticator, BaseCredential
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


class TencentCloudAKSKCredential(BaseCredential):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAuthenticator(BaseAKSKAuthenticator):
    @property
    def credential_type(self) -> Type[TencentCloudAKSKCredential]:
        return TencentCloudAKSKCredential

    def authenticate(self, credential: TencentCloudAKSKCredential):
        pass
