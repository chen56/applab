import shlex
from pathlib import Path

import pytest

from applab.cli.main import ApplabCli
from applab.core import Applab, CloudAccounts, JsonStorage


@pytest.fixture
def mock_applab(tmp_path: Path):
    # 为测试创建一个临时的 applab 环境
    app = Applab(account_storage=JsonStorage(path=tmp_path / "accounts.json", model=CloudAccounts))
    # 保持原有的 vendors 注册，或者根据需要重新注册
    from applab.vendor import tencentcloud

    app.vendors.register(tencentcloud.TencentCloudVendor(version="0.0.1"))
    app.vendors.register(tencentcloud.AliyunVendor(version="0.0.1"))

    return app


@pytest.fixture
def runner(mock_applab: Applab, capsys):
    app = ApplabCli(mock_applab).app

    def _run(cmd: str):
        args = shlex.split(cmd)

        try:
            # Cyclopts app can be called with a list of strings
            exit_code = app(list(args))
        except SystemExit as e:
            exit_code = e.code

        captured = capsys.readouterr()
        return exit_code, captured.out, captured.err

    return _run
