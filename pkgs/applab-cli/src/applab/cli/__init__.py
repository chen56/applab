"""applab.cli.

没有export的模块，只提供cli的入口函数。
"""

version = "0.0.1"

from applab.core import Applab
from applab.vendor import tencentcloud

applab = Applab()
applab.vendors.register(tencentcloud.TencentCloudVendor(version=version))
applab.vendors.register(tencentcloud.AliyunVendor(version=version))

from .main import main

__all__ = ["main"]
