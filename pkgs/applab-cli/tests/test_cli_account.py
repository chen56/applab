from typing import cast

from applab.vendor.tencentcloud import TencentCloudVendor
from unittest.mock import patch

from applab.core import Applab


def test_account_login_tencentcloud_mock(mock_applab: Applab, runner):
    from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
    fake_resp = GetUserAppIdResponse()
    fake_resp.AppId = 12345678
    fake_resp.Uin = "10000001"
    fake_resp.OwnerUin = "10000001"

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient.GetUserAppId") as mock_method:
        mock_method.return_value = fake_resp

        exit_code, out, err = runner(
            "account login tencentcloud --secret-id mock-id --secret-key mock-key --title test-acc"
        )

        mock_method.assert_called_once()
    assert exit_code == 0
    assert "已成功登录" in out
    assert "tencentcloud" in out

    vendor: TencentCloudVendor = cast(TencentCloudVendor, mock_applab.vendors["tencentcloud"])

    accounts = vendor.account_manager.accounts.accounts
    assert len(accounts) == 1
    acc = accounts[0]
    assert acc.vendor == "tencentcloud"
    assert acc.title == "test-acc"


def test_account_list(mock_applab, runner):
    exit_code, out, err = runner("account list")
    assert exit_code == 0
    assert "Cloud Accounts" in out


def test_account_info_help(runner):
    exit_code, out, err = runner("account info --help")
    assert exit_code == 0
    assert "VENDOR" in out