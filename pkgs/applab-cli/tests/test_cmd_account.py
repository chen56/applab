from unittest.mock import patch, MagicMock

from applab.core import Applab
from applab.vendor.tencentcloud.tendentcloud import TencentCloudAKSKCredentialParam, TencentCloudAccount


def test_account_list_empty(runner):
    exit_code, out, err = runner("account list")
    assert exit_code == 0
    assert "Cloud Accounts" in out


def test_account_login_and_list(runner, mock_applab: Applab):
    # Mock the authenticator's response
    mock_resp = MagicMock()
    mock_resp.AppId = 12345
    mock_resp.Uin = "1000001"
    mock_resp.OwnerUin = "1000001"

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.return_value = mock_resp

        # Run the login command
        cmd = "account login tencentcloud --secret-id fake-id --secret-key fake-key --title test-acc"
        exit_code, out, err = runner(cmd)
        assert exit_code == 0
        assert "已成功登录 tencentcloud" in out
        assert "已保存账号到" in out

    # Run the list command to verify the account was saved
    exit_code, out, err = runner("account list")
    assert exit_code == 0
    assert "Cloud Accounts" in out
    assert "tencentcloud" in out
    assert "test-acc" in out

    # Run the info command
    exit_code, out, err = runner("account info tencentcloud")
    assert exit_code == 0
    assert "test-acc" in out
    assert "12345" in out
