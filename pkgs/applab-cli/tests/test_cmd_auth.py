import json
from unittest.mock import patch

import pytest

from applab.core import Applab


class TestLogin:
    def test_login_success2(self, runner, mock_applab: Applab, mock_tencent_auth):
        """Tests successful login and credential storage."""
        # mock_auth, mock_account = mock_tencent_auth
        exit_code, out, err = runner(mock_applab,
                                     "auth login tencentcloud --secret-id mock-id --secret-key mock-key")

        assert exit_code == 0
        assert "已成功登录 tencentcloud" in out
        storage_path = mock_applab.vendors["tencentcloud"].auth_manager._storage.path
        assert "已保存认证信息到" in out
        assert "tencentcloud.json" in out

        # Verify the content of the JSON file
        print(f"storage_path: {storage_path}")
        with open(storage_path, 'r') as f:
            data = json.load(f)
        assert len(data["auths"]) == 1
        stored_acc_data = data["auths"][0]
        assert stored_acc_data["title"] == "default-mock"
        assert stored_acc_data["app_id"] == 999
        assert stored_acc_data["secret_id"] == "mock-id"
        assert stored_acc_data["secret_key"] == "mock-key"  # pydantic serializes SecretStr to str

    def test_login_success(self, runner, mock_applab: Applab, monkeypatch):
        """Tests successful login and credential storage."""
        # mock_auth, mock_account = mock_tencent_auth
        from tencentcloud.cam.v20190116.models import GetUserAppIdResponse
        fake_resp = GetUserAppIdResponse()
        fake_resp.AppId = 12345678
        fake_resp.Uin = "10000001"
        fake_resp.OwnerUin = "10000001"

        from tencentcloud.cam.v20190116.cam_client import CamClient
        monkeypatch.setattr(CamClient, "GetUserAppId", lambda _, __: fake_resp)

        exit_code, out, err = runner(mock_applab,
                                     "auth login tencentcloud --secret-id mock-id --secret-key mock-key")

        assert exit_code == 0
        assert "已成功登录 tencentcloud" in out
        storage_path = mock_applab.vendors["tencentcloud"].auth_manager._storage.path
        assert "已保存认证信息到" in out
        assert "tencentcloud.json" in out

        # Verify the content of the JSON file
        print(f"storage_path: {storage_path}")
        with open(storage_path, 'r') as f:
            data = json.load(f)
        assert len(data["auths"]) == 1
        stored_acc_data = data["auths"][0]
        assert stored_acc_data["title"] == "default"
        assert stored_acc_data["app_id"] == 12345678
        assert stored_acc_data["secret_id"] == "mock-id"
        assert stored_acc_data["secret_key"] == "mock-key"  # pydantic serializes SecretStr to str

    @pytest.mark.parametrize(
        "mock_tencent_auth", [Exception("Authentication failed!")], indirect=True
    )
    def test_login_failure(self, runner, mock_applab: Applab, mock_tencent_auth):
        """Tests failed login."""
        cmd = "auth login tencentcloud --secret-id bad-id --secret-key bad-key"
        exit_code, out, err = runner(mock_applab, cmd)
        assert exit_code == 1
        assert "Authentication failed!" in out


class TestList:
    def test_list_empty(self, runner, mock_applab: Applab):
        """Tests listing with no auths."""
        exit_code, out, err = runner(mock_applab, "auth list")
        assert exit_code == 0
        assert "Cloud Auths" in out
        # Ensure no auth rows are printed
        assert "test-auth-1" not in out

    def test_list_with_auths(self, runner, prefilled_applab: Applab):
        """Tests listing with multiple pre-filled auths."""
        exit_code, out, err = runner(prefilled_applab, "auth list")
        assert exit_code == 0
        assert "Cloud Auths" in out
        assert "test-auth-1" in out
        assert "tc-id-12345" in out
        assert "test-auth-2" in out
        assert "tc-id-67890" in out
        assert "ambiguous-title" in out


class TestInfo:
    def test_info_by_id(self, runner, prefilled_applab: Applab):
        exit_code, out, err = runner(prefilled_applab, "auth info tc-id-12345")
        assert exit_code == 0
        assert "test-auth-1" in out
        assert "secret_key=SecretStr('**********')" in out  # Pydantic's repr for SecretStr

    def test_info_by_title(self, runner, prefilled_applab: Applab):
        exit_code, out, err = runner(prefilled_applab, "auth info test-auth-2")
        assert exit_code == 0
        assert "test-auth-2" in out
        assert "tc-id-67890" in out

    def test_info_not_found(self, runner, prefilled_applab: Applab):
        exit_code, out, err = runner(prefilled_applab, "auth info non-existent-id")
        assert exit_code == 1
        assert "未找到指定的认证信息 'non-existent-id'" in out

    def test_info_ambiguous_title(self, runner, prefilled_applab: Applab):
        exit_code, out, err = runner(prefilled_applab, "auth info ambiguous-title")
        assert exit_code == 1
        assert "找到多个名为 'ambiguous-title' 的认证信息" in out


class TestLogout:
    @patch("rich.prompt.Confirm.ask", return_value=True)
    def test_logout_by_id_confirmed(self, mock_ask, runner, prefilled_applab: Applab):
        manager = prefilled_applab.vendors["tencentcloud"].auth_manager
        assert manager.find_by_id("tc-id-12345") is not None

        exit_code, out, err = runner(prefilled_applab, "auth logout tc-id-12345")
        assert exit_code == 0
        assert "已成功删除认证信息 'test-auth-1'" in out
        assert manager.find_by_id("tc-id-12345") is None

    @patch("rich.prompt.Confirm.ask", return_value=False)
    def test_logout_by_title_cancelled(self, mock_ask, runner, prefilled_applab: Applab):
        manager = prefilled_applab.vendors["tencentcloud"].auth_manager
        assert manager.find_by_id("tc-id-67890") is not None

        exit_code, out, err = runner(prefilled_applab, "auth logout test-account-2")
        assert "未找到指定的认证信息" in out
        assert exit_code == 1
        assert manager.find_by_id("tc-id-67890") is not None

    def test_logout_not_found(self, runner, prefilled_applab: Applab):
        exit_code, out, err = runner(prefilled_applab, "auth logout non-existent-id")
        assert exit_code == 1
        assert "未找到指定的认证信息" in out
