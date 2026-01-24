import inspect
from typing import Optional

from applab.core import Account, Applab, Authenticator, Vendor
from cyclopts import App

from ._console import console


class AccountApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="account",
            help="""
            Cloud account management.
            """,
        )
        self.app.command(self.list_, name="list")
        self.app.command(self.info)
        self.app.command(self.logout)
        self.app.command(AccountLoginApp(applab).app, name="login")

    # todo 是否能重构到core内部去
    def _find_account(self, auth_id: str) -> Optional[tuple[Vendor, Account]]:
        found_accounts = []
        for vendor in self.applab.vendors.values():
            for acc in vendor.account_manager.accounts:
                if acc.account_id == auth_id or acc.title == auth_id:
                    found_accounts.append((vendor, acc))
        if not found_accounts:
            console.error(f"未找到指定的账户 '{auth_id}'。")
            return None
        if len(found_accounts) > 1:
            console.error(
                f"找到多个名为 '{auth_id}' 的账户，请使用唯一的账户 ID 执行。"
            )
            return None
        return found_accounts[0]

    def list_(self):
        """
        列出所有已保存的云账户信息。
        """
        from rich.table import Table

        table = Table(title="Cloud Accounts", show_lines=True)
        table.add_column("Vendor")
        table.add_column("Account Name")
        table.add_column("Account ID")
        table.add_column("Default")
        table.add_column("Created At")
        for vendor in self.applab.vendors.values():
            for acc in vendor.account_manager._accounts.accounts:
                table.add_row(
                    acc.vendor,
                    acc.title,
                    acc.account_id,
                    str(acc.is_default),
                    str(acc.created_at),
                )
        console.print(table)

    # todo 重构account_spec 名为auth_id
    def info(self, account_spec: str):
        """
        展示指定账户的详细信息。
        """
        result = self._find_account(account_spec)
        if not result:
            return 1
        _, acc = result
        console.print(acc)
        return 0

    # todo 重构account_spec 名为auth_id
    def logout(self, account_spec: str):
        """
        删除一个已保存的云账户。
        """
        result = self._find_account(account_spec)
        if not result:
            return 1

        from rich.prompt import Confirm

        vendor, acc = result
        console.print("即将删除以下账户，该操作会一并删除本地保存的凭据，且不可恢复！")
        console.print(acc)
        if not Confirm.ask("请确认是否删除该账户", default=False):
            console.info("操作已取消。")
            return 0

        removed = vendor.account_manager.remove(acc.account_id)
        if removed:
            console.success(f"已成功删除账户 '{removed.title}' (ID: {removed.account_id})。")
        else:
            console.error(f"删除账户 '{acc.title}' (ID: {acc.account_id}) 时发生错误。")
            return 1
        return 0


class AccountLoginApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="login",
            help="""
                Cloud account login.
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

                    account = authenticator.authenticate(credential_param)
                    console.success(f"已成功登录 {vendor.name}")
                    vendor.account_manager.add(account)
                    console.info(f"已保存账号到 {vendor.account_manager._storage.path}")
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
