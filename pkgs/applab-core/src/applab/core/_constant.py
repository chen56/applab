from pathlib import Path
from typing import NamedTuple


class APPLAB(NamedTuple):
    APP_NAME = ("applab",)


class _APPLAB(NamedTuple):
    APP_NAME = APPLAB.APP_NAME
    CONFIG_DIR = Path.home().joinpath(".applab")
    ACCOUNTS_FILE = CONFIG_DIR.joinpath("accounts.json")
