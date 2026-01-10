from typing import Annotated, Type

from pydantic import Field
from pydantic.types import SecretStr

from applab.core import Authenticator, CredentialParam, Account, Vendor, AccountManager
from applab.core import AccountList
from applab.core import APPLAB
from applab.core.storage import JsonStorage


class TencentCloudVendor(Vendor):
    def __init__(self, version: str):
        super().__init__(
            name="tencentcloud",
            display_name="腾讯云",
            version=version,
            authenticator=TencentCloudAKSKAuthenticator(),
            account_manager=AccountManager(
                storage=JsonStorage(path=APPLAB.CONFIG_DIR / "tencentcloud.json", model=AccountList[TencentCloudAccount]),
            ),
        )


class TencentCloudAKSKCredentialParam(CredentialParam):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAccount(Account):
    vendor: str = "tencentcloud"
    app_id: int
    uin: str
    owner_uin: str


class TencentCloudAKSKAuthenticator(Authenticator):
    @property
    def credential_type(self) -> Type[TencentCloudAKSKCredentialParam]:
        return TencentCloudAKSKCredentialParam

    def authenticate(self, credential_param: TencentCloudAKSKCredentialParam):
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.cam.v20190116 import cam_client as cam, models as cam_models
        try:
            cred = credential.Credential(credential_param.secret_id, credential_param.secret_key.get_secret_value())

            client = cam.CamClient(cred, "ap-guangzhou")
            req = cam_models.GetUserAppIdRequest()
            resp = client.GetUserAppId(req)
            result = TencentCloudAccount(
                title=credential_param.title,
                app_id=resp.AppId,
                uin=resp.Uin,
                owner_uin=resp.OwnerUin,
            )

            return result
        except TencentCloudSDKException as err:
            print(f"登录失败: {err}")
            raise err
