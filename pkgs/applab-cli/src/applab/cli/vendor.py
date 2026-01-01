from cyclopts import App

from applab.core import applab

from ._common import cli

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

    table = Table(title="Demo Table", show_lines=True)
    table.add_column("Name")
    table.add_column("Version")

    for vendor in applab.runtimes.values():
        table.add_row(vendor.name, vendor.version)
    print(table)


@account_app.command
def info(vendor:str):
    """vendor metadata."""
    if vendor not in applab.runtimes:
        cli.error(f"Vendor {vendor} not found.")
        return 1  # 返回非零退出码表示失败
    cli.print(applab.runtimes[vendor])

@account_app.command
def login(path, url):
    """Upload a file."""
    print(f"Downloading {url} to {path}.")
