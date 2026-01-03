from cyclopts import App

from applab.core import applab

from ._console import console

account_app = App(
    name="account",
    help="""
Cloud vendor account management.
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

    for vendor in applab.vendors.values():
        table.add_row(vendor.name, vendor.version)
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
Cloud vendor account login.
""",
)


# 动态为每个云厂商生成登录命令
for vendor in applab.vendors.values():
    # 定义登录函数
    def login_vendor(vendor_name=vendor.name):
        """登录指定云厂商"""
        #     password=getpass.getpass("Password: ")
        console.info(f"正在登录 {vendor_name}...")
        # 这里可以添加实际的登录逻辑
        # 如果 VendorBase 类有 login 方法，可以调用：applab.vendors[vendor_name].login()
        console.success(f"已成功登录 {vendor_name}")
        return 0
    # 动态注册命令，使用 vendor.name 作为命令名
    login_app.command(name=vendor.name)(login_vendor)
account_app.command(login_app)
