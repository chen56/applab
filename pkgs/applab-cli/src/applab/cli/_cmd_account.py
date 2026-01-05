import inspect

from cyclopts import App, Parameter
from applab.core import Vendor, Authenticator
from . import applab
from ._console import console

account_app = App(
    name="account",
    help="""
Cloud account management.
""",
)


@account_app.command(name="list")
def list_():
    """
    List all vendors.
    """
    from rich.table import Table

    table = Table(title="account table", show_lines=True)
    table.add_column("Vendor")
    table.add_column("Version")

    for v in applab.vendors.values():
        table.add_row(v.name, v.version)
    console.print(table)


@account_app.command
def info(vendor: str):
    """vendor metadata."""
    if vendor not in applab.vendors:
        console.error(f"Vendor {vendor} not found.")
        return 1  # 返回非零退出码表示失败
    console.print(applab.vendors[vendor])
    return 0


login_app = App(
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
        account=authenticator.authenticate(param)
        console.success(f"已成功登录 {vendor.name}")

        accounts=applab.account_storage.load()
        accounts.add(account)
        # cloudAccounts.
        applab.account_storage.save_account(accounts)
        # 执行实际逻辑
        return 0

    return login_handler


# 动态为每个云厂商生成登录命令
for vendor in applab.vendors.values():
    a = vendor.default_authenticator
    if a:
        authenticator_doc = inspect.cleandoc(a.__doc__ or "")
        cmd_help = f"""
{vendor.display_name}({vendor.name}) login.

**认证逻辑:**

{authenticator_doc}
        """
        login_app.command(name=vendor.name, help=inspect.cleandoc(cmd_help or ""))(_create_login_handler(vendor, a))

account_app.command(login_app)
