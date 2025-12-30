import pytest

from examples.hello.main import TencentCloudProvider


@pytest.fixture(scope="session")
def app_config():
    x: TencentCloudProvider = TencentCloudProvider()
