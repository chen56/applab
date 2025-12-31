"""applab.cli.

没有export的模块，只提供cli的入口函数。
"""

from .main import main

__all__ = ["main"]

from applab.core import applab

from applab.vendor import tencentcloud

applab.runtimes.register(tencentcloud.TencentCloudVendor(name="tencentcloud", version="0.0.1"))
