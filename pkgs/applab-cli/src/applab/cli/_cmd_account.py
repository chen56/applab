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
        List all vendors.
        """
        from rich.table import Table

        table = Table(title="account table", show_lines=True)
        table.add_column("Vendor")
        table.add_column("Version")

        for v in self.applab.vendors.values():
            table.add_row(v.name, v.version)
        console.print(table)

    def info(self, vendor: str):
        """vendor metadata."""
        if vendor not in self.applab.vendors:
            console.error(f"Vendor {vendor} not found.")
            return 1  # 返回非零退出码表示失败
        console.print(self.applab.vendors[vendor])
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

        # 动态为每个云厂商生成登录命令
        for vendor in applab.vendors.values():
            a = vendor.authenticator
            if a:
                authenticator_doc = inspect.cleandoc(a.__doc__ or "")
                cmd_help = f"""
                    {vendor.display_name}({vendor.name}) login.
                    
                    **认证逻辑:**
                    
                    {authenticator_doc}
                """
                self.app.command(name=vendor.name, help=inspect.cleandoc(cmd_help or ""))(
                    self._create_login_handler(vendor, a))

    def _create_login_handler(self, vendor: Vendor, authenticator: Authenticator):
        @Parameter(name="*")
        class DynamicParam(authenticator.credential_type):
            pass

        def login_handler(*, param: DynamicParam):
            console.info(f"正在登录 {vendor.name}...{param=}")
            account = authenticator.authenticate(param)
            console.success(f"已成功登录 {vendor.name}")

            accounts = self.applab.account_storage.load()
            accounts.add(account)
            # cloudAccounts.
            self.applab.account_storage.save(accounts)
            console.info(f"已保存账号 {self.applab.account_storage.path}")
            # 执行实际逻辑
            return 0

        return login_handler
