from cyclopts import App
from rich.console import Console

from applab.core import applab

console = Console(width=80)
print = console.print

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
def info(path, url):
    """vendor metadata."""
    print(f"Downloading {url} to {path}.")


@account_app.command
def login(path, url):
    """Upload a file."""
    print(f"Downloading {url} to {path}.")
