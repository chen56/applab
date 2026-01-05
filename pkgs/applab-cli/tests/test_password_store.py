import pytest


@pytest.fixture(scope="session")
def app_config():
    assert 1 == 1


def test_login_success(app_config):
    assert 1 == 1
