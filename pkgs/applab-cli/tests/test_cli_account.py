import shlex
from typing import Iterable
from unittest.mock import patch, Mock

from applab.cli.main import ApplabCli
from applab.core import Applab


class AccountFixture:
    def __init__(self, applab: Applab,capsys):
        self.applab = applab
        self.capsys=capsys

    def assert_login(self, *, cmd: str, out: str | None = None, accounts: Iterable = ()):
        from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
        mock_resp = Mock(spec=GetUserAppIdResponse, AppId=123, Uin="101", OwnerUin="101")

        with patch("tencentcloud.cam.v20190116.cam_client.CamClient.GetUserAppId") as mock_method:
            mock_method.return_value = mock_resp

            # 执行测试

            # 验证：顺便检查一下 SDK 是不是真的被调用了，参数对不对
            mock_method.assert_called_once()

    def run(self, cmd: str):
        args = shlex.split(cmd)
        app = ApplabCli(self.applab).app

        try:
            # Cyclopts app can be called with a list of strings
            exit_code = app(list(args))
        except SystemExit as e:
            exit_code = e.code

        captured = self.capsys.readouterr()
        return exit_code, captured.out, captured.err


def test_account_login(account_fixture: AccountFixture):
    account_fixture.assert_login(
        cmd="account login tencentcloud --secret-id mock-id --secret-key mock-key --name test-acc",
        accounts=(),
    )


def test_account_login_tencentcloud_mock(mock_applab, runner):
    from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
    fake_resp = GetUserAppIdResponse()
    fake_resp.AppId = 12345678
    fake_resp.Uin = "10000001"
    fake_resp.OwnerUin = "10000001"

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient.GetUserAppId") as mock_method:
        mock_method.return_value = fake_resp

        # 执行测试
        exit_code, out, err = runner(
            "account login tencentcloud --secret-id mock-id --secret-key mock-key --name test-acc"
        )

        # 验证：顺便检查一下 SDK 是不是真的被调用了，参数对不对
        mock_method.assert_called_once()
    assert exit_code == 0
    # 验证输出中包含成功信息 (console.success 输出到 stderr)
    assert "已成功登录" in err
    assert "tencentcloud" in err

    # 验证存储中是否真的保存了账号
    accounts = mock_applab.account_storage.load()
    assert len(accounts.accounts) == 1
    acc = accounts.accounts[0]
    assert acc.vendor == "tencentcloud"
    assert acc.name == "test-acc"

    # 检查是否成功调用了 authenticator
    # (如果以后需要验证参数，可以在这里增加断言)


def test_account_list(mock_applab, runner):
    exit_code, out, err = runner("account list")
    assert exit_code == 0
    assert "tencentcloud" in out
    assert "aliyun" in out


def test_account_info_help(runner):
    exit_code, out, err = runner("account info --help")
    assert exit_code == 0
    assert "VENDOR" in out
    assert "vendor metadata" in out
