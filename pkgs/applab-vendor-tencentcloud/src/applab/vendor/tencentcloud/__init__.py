"""
Tencent Cloud Provider

[tencentcloud-sdk-python](https://github.com/TencentCloud/tencentcloud-sdk-python)
"""

from .tendentcloud import TencentCloudVendor
from .aliyun import AliyunVendor

__all__ = [
    "TencentCloudVendor",
    "AliyunVendor",
]
