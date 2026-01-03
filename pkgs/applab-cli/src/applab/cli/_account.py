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

    for vendor in applab.runtimes.values():
        table.add_row(vendor.name, vendor.version)
    console.print(table)


@account_app.command
def info(vendor: str):
    """vendor metadata."""
    if vendor not in applab.runtimes:
        console.error(f"Vendor {vendor} not found.")
        return 1  # 返回非零退出码表示失败
    console.print(applab.runtimes[vendor])
    return 0


@account_app.command
def login():
    """Upload a file."""
    console.info(f"Downloading .")
