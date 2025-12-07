"""测试qpa.core模块的功能."""

from qpa import core


def test_say_hello():
    """测试say_hello函数返回正确的问候语格式."""
    assert core.say_hello("Alice") == "Hello, Alice! 这是根目录包结构的示例"


def test_say_goodbye():
    """测试say_goodbye函数返回正确的告别语格式."""
    assert core.say_goodbye("Bob") == "Goodbye, Bob! 欢迎下次使用"
