from qpa import core


def test_say_hello():
    assert core.say_hello("Alice") == "Hello, Alice! 这是根目录包结构的示例"


def test_say_goodbye():
    assert core.say_goodbye("Bob") == "Goodbye, Bob! 欢迎下次使用"
