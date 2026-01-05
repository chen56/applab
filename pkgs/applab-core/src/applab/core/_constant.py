from pathlib import Path
from typing import NamedTuple


class APPLAB(NamedTuple):
    APP_NAME = "applab",


class _APPLAB(NamedTuple):
    APP_NAME = APPLAB.APP_NAME,
    CONFIG_DIR = Path(Path.home(), ".applab")
    ACCOUNTS_FILE = Path(CONFIG_DIR, ".accounts.json"),
