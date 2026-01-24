from typing import Annotated, Literal, Type

from applab.core import (
    APPLAB,
    AuthInfo,
    AuthInfoList,
    AuthManager,
    Authenticator,
    CredentialParam,
    Vendor,
)
from applab.core._model import AppLabBase
from applab.core.storage import JsonStorage
from pydantic import Field
from pydantic.types import SecretStr


class TencentCloudVendor(Vendor):
    def __init__(
        self,
        version: str,
        auth_manager: AuthManager["TencentCloudAuthInfo"] | None = None,
    ):
        # todo 没必要提供 可选的auth_manager,test时可以mock改APPLAB.CONFIG_DIR
        if auth_manager is None:
            auth_manager = AuthManager(
                storage=JsonStorage(
                    path=APPLAB.CONFIG_DIR / "tencentcloud.json",
                    model=AuthInfoList[TencentCloudAuthInfo],
                )
            )
        super().__init__(
            name="tencentcloud",
            display_name="腾讯云",
            version=version,
            authenticator=TencentCloudAKSKAuthenticator(),
            auth_manager=auth_manager,
        )


class TencentCloudAKSKCredentialParam(CredentialParam):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAccountInfo(AppLabBase):
    app_id: int
    uin: str
    owner_uin: str


class TencentCloudAKSKCredential(AppLabBase):
    # XXX(P2): 加密secret_key
    secret_id: str
    secret_key: SecretStr


class TencentCloudAuthInfo(AuthInfo):
    vendor: Literal["tencentcloud"] = "tencentcloud"
    account: TencentCloudAccountInfo
    credential: TencentCloudAKSKCredential


class TencentCloudAKSKAuthenticator(Authenticator):
    @property
    def credential_type(self) -> Type[TencentCloudAKSKCredentialParam]:
        return TencentCloudAKSKCredentialParam

    def authenticate(self, credential_param: TencentCloudAKSKCredentialParam):
        from tencentcloud.cam.v20190116 import cam_client as cam
        from tencentcloud.cam.v20190116 import models as cam_models
        from tencentcloud.common import credential

        cred = credential.Credential(
            credential_param.secret_id, credential_param.secret_key.get_secret_value()
        )

        client = cam.CamClient(cred, "ap-guangzhou")
        req = cam_models.GetUserAppIdRequest()
        resp = client.GetUserAppId(req)

        account = TencentCloudAccountInfo(
            app_id=resp.AppId,
            uin=resp.Uin,
            owner_uin=resp.OwnerUin,
        )

        credential_obj = TencentCloudAKSKCredential(
            secret_id=credential_param.secret_id,
            secret_key=credential_param.secret_key,
        )

        return TencentCloudAuthInfo(
            title=credential_param.title,
            account=account,
            credential=credential_obj,
        )
