from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path

from pydantic import SecretStr

from applab.core import Applab, AuthManager, JsonStorage
# XXX(P2): 测试代码引用内部module不应该报问题
from applab.core._auth import AuthInfoList
from applab.vendor.tencentcloud.tendentcloud import TencentCloudVendor, TencentCloudAKSKCredentialParam, \
    TencentCloudAuthInfo, TencentCloudAKSKAuthenticator, TencentCloudAccountInfo, TencentCloudAKSKCredential


class Fixture:
    def __init__(self, *, applab: Applab, vendor: TencentCloudVendor):
        self.applab = applab
        self.vendor = vendor
        self.applab.vendors.register(self.vendor)


@pytest.fixture
def fixture(tmp_path: Path):
    applab = Applab()
    # TODO 范型检查问题，需调查解决
    storage = JsonStorage(path=tmp_path / "tencentcloud.json", model=AuthInfoList[TencentCloudAuthInfo])
    auth_manager = AuthManager(storage=storage)
    vendor = TencentCloudVendor(version="0.0.1", auth_manager=auth_manager)
    return Fixture(applab=applab, vendor=vendor)


def test_login_success(fixture: Fixture):
    authenticator = fixture.vendor.authenticator
    assert isinstance(authenticator, TencentCloudAKSKAuthenticator)

    mock_resp = MagicMock()
    mock_resp.AppId = 12345
    mock_resp.Uin = "1000001"
    mock_resp.OwnerUin = "1000001"

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.return_value = mock_resp

        credential_param = TencentCloudAKSKCredentialParam(
            title="test_account",
            secret_id="AKIDtest",
            secret_key=SecretStr("secret")
        )

        a = authenticator.authenticate(credential_param)
        # TODO 范型检查问题，需调查解决
        fixture.vendor.auth_manager.add(a)

        assert isinstance(a, TencentCloudAuthInfo)
        assert a.title == "test_account"
        assert a.account.app_id == 12345
        assert a.account.uin == "1000001"
        assert a.account.owner_uin == "1000001"
        assert a.vendor == "tencentcloud"

        loaded_accounts = fixture.vendor.auth_manager._storage.load()
        assert len(loaded_accounts.auths) == 1
        assert loaded_accounts.auths[0].title == "test_account"


def test_login_failure(fixture: Fixture):
    authenticator = fixture.vendor.authenticator

    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.side_effect = TencentCloudSDKException("AuthFailure", "Invalid SecretId")

        credential_param = TencentCloudAKSKCredentialParam(
            title="test_account",
            secret_id="wrong_id",
            secret_key=SecretStr("wrong_key"),
        )

        with pytest.raises(TencentCloudSDKException):
            authenticator.authenticate(credential_param)

        loaded_accounts = fixture.vendor.auth_manager._storage.load()
        assert len(loaded_accounts.auths) == 0
