"""package.

...
"""

__version__ = "0.0.1dev20251209110701"

# 从_dag模块导入topological_sort_dfs函数，使其成为公共API
from ._dag import _topo_sort


# core.py：包的功能实现模块
def planc_say_hello(name: str) -> str:
    """向指定名字的人打招呼."""
    return f"Hello, {name}! 这是根目录包结构的示例"


# 显式声明公共API，提高代码可读性和安全性
__all__ = [
    "_topo_sort",
    "planc_say_hello",
    "__version__",
]
