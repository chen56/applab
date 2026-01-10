from unittest.mock import MagicMock, patch
import pytest

from applab.core import Applab
from applab.vendor.tencentcloud.tendentcloud import TencentCloudVendor, TencentCloudAKSKCredentialParam, \
    TencentCloudAccount, TencentCloudAKSKAuthenticator


class Fixture:
    def __init__(self, *, applab: Applab):
        self.applab = applab
        self.vendor = TencentCloudVendor(version="0.0.1")
        self.applab.vendors.register(self.vendor)


@pytest.fixture(scope="session")
def fixture():
    applab = Applab()
    return Fixture(applab=applab)


def test_login_success(fixture: Fixture):
    authenticator = fixture.vendor.authenticator
    assert isinstance(authenticator, TencentCloudAKSKAuthenticator)

    # 模拟 SDK 的响应
    mock_resp = MagicMock()
    mock_resp.AppId = 12345
    mock_resp.Uin = "1000001"
    mock_resp.OwnerUin = "1000001"

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.return_value = mock_resp

        credential_param = TencentCloudAKSKCredentialParam(
            name="test_account",
            secret_id="AKIDtest",
            secret_key="secret"
        )

        account = authenticator.authenticate(credential_param)

        assert isinstance(account, TencentCloudAccount)
        assert account.name == "test_account"
        assert account.app_id == 12345
        assert account.uin == "1000001"
        assert account.owner_uin == "1000001"
        assert account.vendor == "tencentcloud"


def test_login_failure(fixture: Fixture):
    authenticator = fixture.vendor.authenticator

    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.side_effect = TencentCloudSDKException("AuthFailure", "Invalid SecretId")

        credential_param = TencentCloudAKSKCredentialParam(
            name="test_account",
            secret_id="wrong_id",
            secret_key="wrong_key"
        )

        with pytest.raises(TencentCloudSDKException):
            authenticator.authenticate(credential_param)
