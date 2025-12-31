from typing import Annotated

from pydantic import BaseModel

from applab.core import TextField, VendorBase

# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================


class TencentCloudCredential(BaseModel):
    secret_id: Annotated[
        str,
        TextField(
            label="SecretId",
            type="text",
            help="Tencent Cloud API SecretId",
        ),
    ]

    secret_key: Annotated[str, TextField(label="SecretKey", type="password", help="Tencent Cloud API SecretKey")]


class TencentCloudVendor(VendorBase):
    def __init__(self, name: str, version: str):
        super().__init__(name=name, version=version)
