from typing import cast

from applab.core import Applab
from applab.vendor.tencentcloud import TencentCloudVendor


def test_account_login_tencentcloud_mock(mock_applab: Applab, runner, monkeypatch):
    from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
    fake_resp = GetUserAppIdResponse()
    fake_resp.AppId = 12345678
    fake_resp.Uin = "10000001"
    fake_resp.OwnerUin = "10000001"

    from tencentcloud.cam.v20190116.cam_client import CamClient
    monkeypatch.setattr(CamClient, "GetUserAppId", lambda _, __: fake_resp)

    exit_code, out, err = runner(
        mock_applab,
        "account login tencentcloud --secret-id mock-id --secret-key mock-key",
    )

    assert "已成功登录" in out
    assert "tencentcloud" in out
    assert exit_code == 0

    vendor: TencentCloudVendor = cast(TencentCloudVendor, mock_applab.vendors["tencentcloud"])

    accounts = vendor.account_manager._accounts.accounts
    assert len(accounts) == 1
    acc = accounts[0]
    assert acc.vendor == "tencentcloud"
    assert acc.title == "default"


def test_account_list(mock_applab, runner):
    exit_code, out, err = runner(mock_applab, "account list")
    assert exit_code == 0
    assert "Cloud Accounts" in out


def test_account_info_help(mock_applab, runner):
    exit_code, out, err = runner(mock_applab, "account info --help")
    assert exit_code == 0
    assert "ACCOUNT-SPEC" in out
