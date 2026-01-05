from typing import Literal
import datetime
from typing import Annotated, Type

from pydantic import Field
from pydantic.types import SecretStr

from applab.core import Authenticator, CredentialParam, CloudAccount
from applab.core import Vendor


# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================
class TencentCloudVendor(Vendor):

    def __init__(self, version: str):
        super().__init__(
            name="tencentcloud",
            display_name="腾讯云",
            version=version,
            default_authenticator=TencentCloudAKSKAuthenticator(),
        )


class TencentCloudAKSKCredentialParam(CredentialParam):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAccount(CloudAccount):
    vendor: Literal["tencentcloud"] = "tencentcloud"
    app_id: int
    uin: str
    owner_uin: str

class TencentCloudAKSKAuthenticator(Authenticator):
    """
    腾讯云 AK/SK (API 密钥) 认证器。

    使用此认证器需要提供腾讯云账号的 `SecretId` 和 `SecretKey`。

    **如何获取密钥：**
    1.  **注册/登陆腾讯云官网**：访问 <https://console.cloud.tencent.com>
    2.  **第一次充值**：需少量充值5~10元(可退): <https://console.cloud.tencent.com/expense>
    3.  **创建密钥**： <https://console.cloud.tencent.com/cam/capi>
        * 点击“新建密钥”。
        * 系统会生成一对 `SecretId` 和 `SecretKey`。
    4.  **登陆applab**：
        * UI 登陆: 打开applab后， 账号管理 -> 腾讯云 -> 输入密钥。
        * 命令行登陆: `applab account login tencentcloud`。

    **注意事项:**
    * 请妥善保管您的 `SecretKey`，不要将其上传到 GitHub 等公开平台。
    * 如果密钥泄露，请立即在控制台删除该密钥。
    * **权限建议**：为了安全起见，建议创建一个 **子账号 (User)** 并仅授予该子账号必要的资源操作权限（如 `QcloudCVMFullAccess`），然后为该子账号创建 API 密钥。

    """

    @property
    def credential_type(self) -> Type[TencentCloudAKSKCredentialParam]:
        return TencentCloudAKSKCredentialParam

    def authenticate(self, credential_param: TencentCloudAKSKCredentialParam):
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.cam.v20190116 import cam_client, models as cam_models

        try:
            cred = credential.Credential(credential_param.secret_id, credential_param.secret_key.get_secret_value())

            client = cam_client.CamClient(cred, "ap-guangzhou")
            req = cam_models.GetUserAppIdRequest()
            resp = client.GetUserAppId(req)

            return TencentCloudAccount(
                name=credential_param.name,
                app_id=resp.AppId,
                uin=resp.Uin,
                owner_uin=resp.OwnerUin,
                verified=True,
                verified_at=datetime.datetime.now(datetime.UTC),)

            # todo exception handling & async support
        except TencentCloudSDKException as err:
            print(f"登录失败: {err}")
            raise err
