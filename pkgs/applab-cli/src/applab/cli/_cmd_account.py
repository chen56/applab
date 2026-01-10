import inspect

from cyclopts import App, Parameter
from applab.core import Vendor, Authenticator, Applab
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
        self.app.command(AccountLoginApp(applab).app, name="login")

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
            for acc in vendor.account_manager.accounts.accounts:
                table.add_row(acc.vendor, acc.title, acc.id, str(acc.is_default), str(acc.created_at))
        console.print(table)

    def info(self, vendor_name: str):
        """
        展示指定云厂商的账户详情（优先展示默认账户）。
        """
        vendor = self.applab.vendors.get(vendor_name)
        if not vendor or not vendor.account_manager or not vendor.account_manager.accounts.accounts:
            console.error(f"未找到厂商 {vendor_name} 的账户信息。")
            return 1

        accounts = vendor.account_manager.accounts.accounts
        default_acc = next((a for a in accounts if a.is_default), accounts[0])
        console.print(default_acc)
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
            @Parameter(name="*")
            class DynamicParam(authenticator.credential_type):
                pass

            def login_handler(*, param: DynamicParam):

                console.info(f"正在登录 {vendor.name}...{param=}")
                account = authenticator.authenticate(param)
                console.success(f"已成功登录 {vendor.name}")
                vendor.account_manager.add(account)
                console.info(f"已保存账号到 {vendor.account_manager.storage.path}")
                return 0

            return login_handler

        for vendor in applab.vendors.values():
            authenticator_doc = inspect.cleandoc(vendor.authenticator.__doc__ or "")
            cmd_help = f"""
                {vendor.display_name}({vendor.name}) login.

                **认证逻辑:**

                {authenticator_doc}
            """
            self.app.command(name=vendor.name, help=inspect.cleandoc(cmd_help or ""))(
                _create_login_handler(vendor, vendor.authenticator))
