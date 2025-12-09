import planc


def test_say_hello():
    """测试say_hello函数返回正确的问候语格式."""
    assert planc.planc_say_hello("Alice") == "Hello, Alice! 这是根目录包结构的示例"
