from typing import cast

from applab.core import Applab
from applab.vendor.tencentcloud import TencentCloudVendor


def test_auth_login_tencentcloud_mock(mock_applab: Applab, runner, monkeypatch):
    from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
    fake_resp = GetUserAppIdResponse()
    fake_resp.AppId = 12345678
    fake_resp.Uin = "10000001"
    fake_resp.OwnerUin = "10000001"

    from tencentcloud.cam.v20190116.cam_client import CamClient
    monkeypatch.setattr(CamClient, "GetUserAppId", lambda _, __: fake_resp)

    exit_code, out, err = runner(
        mock_applab,
        "auth login tencentcloud --secret-id mock-id --secret-key mock-key",
    )

    assert "已成功登录" in out
    assert "tencentcloud" in out
    assert exit_code == 0

    vendor: TencentCloudVendor = cast(TencentCloudVendor, mock_applab.vendors["tencentcloud"])

    auths = vendor.auth_repo._auths.auths
    assert len(auths) == 1
    acc = auths[0]
    assert acc.vendor == "tencentcloud"
    assert acc.title == "default"


def test_auth_list(mock_applab, runner):
    exit_code, out, err = runner(mock_applab, "auth list")
    assert exit_code == 0
    assert "Cloud Auths" in out


def test_auth_info_help(mock_applab, runner):
    exit_code, out, err = runner(mock_applab, "auth info --help")
    assert exit_code == 0
    assert "AUTH-ID" in out
