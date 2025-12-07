"""qpa package.

...
"""

__version__ = "0.1.4"

from .core import say_goodbye, say_hello  # noqa: F401 忽略导入未使用警告

__all__ = ["say_hello", "say_goodbye"]
