import shlex
from pathlib import Path

import pytest

from applab.cli.main import ApplabCli
from applab.core import Applab, AccountManager, JsonStorage
from applab.core._account import AccountList
from applab.vendor.tencentcloud.tendentcloud import TencentCloudVendor, TencentCloudAccount


@pytest.fixture
def mock_applab(tmp_path: Path):
    app = Applab()

    # Setup TencentCloudVendor with a mock AccountManager
    tencent_storage = JsonStorage(path=tmp_path / "tencentcloud.json", model=AccountList[TencentCloudAccount])
    tencent_account_manager = AccountManager(storage=tencent_storage)
    tencent_vendor = TencentCloudVendor(version="0.0.1")
    tencent_vendor.account_manager = tencent_account_manager
    app.vendors.register(tencent_vendor)

    # from applab.vendor import tencentcloud
    # app.vendors.register(tencentcloud.AliyunVendor(version="0.0.1"))

    return app


@pytest.fixture
def runner(mock_applab: Applab, capsys):
    app = ApplabCli(mock_applab).app

    def _run(cmd: str):
        args = shlex.split(cmd)

        try:
            exit_code = app(list(args))
        except SystemExit as e:
            exit_code = e.code

        captured = capsys.readouterr()
        return exit_code, captured.out, captured.err

    return _run
