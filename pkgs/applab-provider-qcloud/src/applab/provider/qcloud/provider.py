from typing import Annotated

from pydantic import BaseModel

from applab.core import TextField, ProviderBase


# ============================================================
# 模拟 applab_apps 包（provider 实现）
# ============================================================

class QCloudCredential(BaseModel):
    secret_id: Annotated[
        str,
        TextField(
            label="SecretId",
            type="text",
            help="Tencent Cloud API SecretId",
        ),
    ]

    secret_key: Annotated[str, TextField(label="SecretKey", type="password", help="Tencent Cloud API SecretKey")]

class QCloudProvider(ProviderBase):
    def __init__(self, name: str, version: str):
        super().__init__(name=name, version=version)
