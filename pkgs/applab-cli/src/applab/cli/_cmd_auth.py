import inspect
from typing import Optional

from applab.core import AuthInfo, Applab, Authenticator, Vendor
from cyclopts import App

from ._console import console


class AuthApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="auth",
            help="""
            Cloud auth management.
            """,
        )
        self.app.command(self.list_, name="list")
        self.app.command(self.info)
        self.app.command(self.logout)
        self.app.command(AuthLoginApp(applab).app, name="login")

    # todo 是否能重构到core内部去
    def _find_auth(self, auth_id: str) -> Optional[tuple[Vendor, AuthInfo]]:
        found_auths = []
        for vendor in self.applab.vendors.values():
            for acc in vendor.auth_repo.auths:
                if acc.auth_id == auth_id or acc.title == auth_id:
                    found_auths.append((vendor, acc))
        if not found_auths:
            console.error(f"未找到指定的认证信息 '{auth_id}'。")
            return None
        if len(found_auths) > 1:
            console.error(
                f"找到多个名为 '{auth_id}' 的认证信息，请使用唯一的 ID 执行。"
            )
            return None
        return found_auths[0]

    def list_(self):
        """
        列出所有已保存的云认证信息。
        """
        from rich.table import Table

        table = Table(title="Cloud Auths", show_lines=True)
        table.add_column("Vendor")
        table.add_column("AuthInfo Name")
        table.add_column("AuthInfo ID")
        table.add_column("Default")
        table.add_column("Created At")
        for vendor in self.applab.vendors.values():
            for acc in vendor.auth_repo._auths.auths:
                table.add_row(
                    acc.vendor,
                    acc.title,
                    acc.auth_id,
                    str(acc.is_default),
                    str(acc.created_at),
                )
        console.print(table)

    def info(self, auth_id: str):
        """
        展示指定认证的详细信息。
        """
        result = self._find_auth(auth_id)
        if not result:
            return 1
        _, acc = result
        console.print(acc)
        return 0

    def logout(self, auth_id: str):
        """
        删除一个已保存的云认证信息。
        """
        result = self._find_auth(auth_id)
        if not result:
            return 1

        from rich.prompt import Confirm

        vendor, acc = result
        console.print("即将删除以下认证信息，该操作会一并删除本地保存的凭据，且不可恢复！")
        console.print(acc)
        if not Confirm.ask("请确认是否删除该认证信息", default=False):
            console.info("操作已取消。")
            return 0

        removed = vendor.auth_repo.remove(acc.auth_id)
        if removed:
            console.success(f"已成功删除认证信息 '{removed.title}' (ID: {removed.auth_id})。")
        else:
            console.error(f"删除认证信息 '{acc.title}' (ID: {acc.auth_id}) 时发生错误。")
            return 1
        return 0


class AuthLoginApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="login",
            help="""
                Cloud auth login.
                """,
        )

        def _create_login_handler(vendor: Vendor, authenticator: Authenticator):
            from typing import Optional  # New import

            from pydantic.types import SecretStr

            def login_handler(
                secret_id: str, secret_key: str, title: Optional[str] = None
            ):
                console.warn("凭据将以明文形式存储在本地 JSON 文件中，请注意安全！")
                console.info(f"正在登录 {vendor.name}...")
                try:
                    credential_param_args = {
                        "secret_id": secret_id,
                        "secret_key": SecretStr(secret_key),
                    }
                    if title is not None:
                        credential_param_args["title"] = title

                    credential_param = authenticator.credential_type(
                        **credential_param_args
                    )

                    auth_info = authenticator.authenticate(credential_param)
                    console.success(f"已成功登录 {vendor.name}")
                    vendor.auth_repo.add(auth_info)
                    console.info(f"已保存认证信息到 {vendor.auth_repo._storage.path}")
                    return 0
                except Exception as e:
                    # todo console 失败一次，会发现颜色字符里有很多乱七八糟的颜色，不知道啥原因?
                    console.error(f"登录失败: {e}")
                    return 1

            return login_handler

        for vendor in applab.vendors.values():
            authenticator_doc = inspect.cleandoc(vendor.authenticator.__doc__ or "")
            cmd_help = f"""
                {vendor.display_name}({vendor.name}) login.

                **认证逻辑:**

                {authenticator_doc}
            """
            self.app.command(name=vendor.name, help=inspect.cleandoc(cmd_help or ""))(
                _create_login_handler(vendor, vendor.authenticator)
            )
