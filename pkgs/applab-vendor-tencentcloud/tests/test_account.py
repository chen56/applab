from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path

from applab.core import Applab, AccountManager, JsonStorage
from applab.core._account import AccountList
from applab.vendor.tencentcloud.tendentcloud import TencentCloudVendor, TencentCloudAKSKCredentialParam, \
    TencentCloudAccount, TencentCloudAKSKAuthenticator


class Fixture:
    def __init__(self, *, applab: Applab, vendor: TencentCloudVendor):
        self.applab = applab
        self.vendor = vendor
        self.applab.vendors.register(self.vendor)


@pytest.fixture
def fixture(tmp_path: Path):
    applab = Applab()
    storage = JsonStorage(path=tmp_path / "tencentcloud.json", model=AccountList[TencentCloudAccount])
    account_manager = AccountManager(storage=storage)
    vendor = TencentCloudVendor(version="0.0.1")
    vendor.account_manager = account_manager
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
            secret_key="secret"
        )

        account = authenticator.authenticate(credential_param)
        fixture.vendor.account_manager.add(account)

        assert isinstance(account, TencentCloudAccount)
        assert account.title == "test_account"
        assert account.app_id == 12345
        assert account.uin == "1000001"
        assert account.owner_uin == "1000001"
        assert account.vendor == "tencentcloud"

        loaded_accounts = fixture.vendor.account_manager.storage.load()
        assert len(loaded_accounts.accounts) == 1
        assert loaded_accounts.accounts[0].title == "test_account"


def test_login_failure(fixture: Fixture):
    authenticator = fixture.vendor.authenticator

    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

    with patch("tencentcloud.cam.v20190116.cam_client.CamClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.GetUserAppId.side_effect = TencentCloudSDKException("AuthFailure", "Invalid SecretId")

        credential_param = TencentCloudAKSKCredentialParam(
            title="test_account",
            secret_id="wrong_id",
            secret_key="wrong_key"
        )

        with pytest.raises(TencentCloudSDKException):
            authenticator.authenticate(credential_param)

        loaded_accounts = fixture.vendor.account_manager.storage.load()
        assert len(loaded_accounts.accounts) == 0
