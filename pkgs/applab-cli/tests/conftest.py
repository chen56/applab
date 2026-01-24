import shlex
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic.types import SecretStr

from applab.cli import _console
from applab.cli.main import ApplabCli
from applab.core import Applab, AccountManager, JsonStorage
from applab.core._account import AccountList
from applab.vendor.tencentcloud.tendentcloud import TencentCloudVendor, TencentCloudAccount


@pytest.fixture
def tencent_vendor(tmp_path: Path) -> TencentCloudVendor:
    """Provides a TencentCloudVendor instance with isolated storage."""
    storage_path = tmp_path / "tencentcloud.json"
    storage = JsonStorage(path=storage_path, model=AccountList[TencentCloudAccount])
    account_manager = AccountManager(storage=storage)
    vendor = TencentCloudVendor(version="0.0.1", account_manager=account_manager)
    return vendor


@pytest.fixture
def mock_applab(tencent_vendor: TencentCloudVendor) -> Applab:
    """Provides an Applab instance with a mocked TencentCloudVendor."""
    app = Applab()
    app.vendors.register(tencent_vendor)
    return app


@pytest.fixture
def prefilled_applab(mock_applab: Applab) -> Applab:
    """Provides an Applab instance with pre-filled account data."""
    manager = mock_applab.vendors["tencentcloud"].account_manager
    acc1 = TencentCloudAccount(
        account_id="tc-id-12345",
        vendor="tencentcloud",
        title="test-account-1",
        app_id=1, uin="1", owner_uin="1",
        secret_id="id1", secret_key=SecretStr("key1")
    )
    acc2 = TencentCloudAccount(
        account_id="tc-id-67890",
        vendor="tencentcloud",
        title="test-account-2",
        app_id=2, uin="2", owner_uin="2",
        secret_id="id2", secret_key=SecretStr("key2")
    )
    acc3 = TencentCloudAccount(
        account_id="tc-id-abcde",
        vendor="tencentcloud",
        title="ambiguous-title",
        app_id=3, uin="3", owner_uin="3",
        secret_id="id3", secret_key=SecretStr("key3")
    )
    acc4 = TencentCloudAccount(
        account_id="tc-id-fghij",
        vendor="tencentcloud",
        title="ambiguous-title",
        app_id=4, uin="4", owner_uin="4",
        secret_id="id4", secret_key=SecretStr("key4")
    )
    manager.add(acc1)
    manager.add(acc2)
    manager.add(acc3)
    manager.add(acc4)
    return mock_applab


@pytest.fixture
def mock_tencent_auth(request):
    """
    Mocks TencentCloudAKSKAuthenticator.authenticate.
    Can be parameterized to return a specific account or raise an exception.
    """
    mock_account = TencentCloudAccount(
        title="default-mock",
        app_id=999, uin="999", owner_uin="999",
        secret_id="mock-id", secret_key=SecretStr("mock-key")
    )

    if hasattr(request, "param"):
        if isinstance(request.param, Exception):
            mock_return = request.param
        else:
            mock_account = request.param
            mock_return = mock_account
    else:
        mock_return = mock_account

    def side_effect(param):
        if isinstance(mock_return, Exception):
            raise mock_return
        return mock_return

    with patch(
            "applab.vendor.tencentcloud.tendentcloud.TencentCloudAKSKAuthenticator.authenticate",
            side_effect=side_effect
    ) as mock:
        yield mock, mock_account


@pytest.fixture
def runner(capsys):
    """
    Provides a function to run CLI commands against a given Applab instance
    and captures the output.
    """

    def run(applab_instance: Applab, cmd: str):
        app = ApplabCli(applab_instance).app
        args = shlex.split(cmd)

        # Resetting stdout/stderr capture
        capsys.readouterr()

        try:
            exit_code = app(list(args))
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0
        except Exception:
            exit_code = 1  # Generic failure
        # todo read了2次？
        captured = capsys.readouterr()
        return exit_code, _console.strip_ansi(captured.out), _console.strip_ansi(captured.err)

    return run
