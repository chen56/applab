"""cli main入口"""
import logging
import os
import sys

from cyclopts import App
from rich.logging import RichHandler

from applab.core import Applab
from applab.vendor import tencentcloud
from ._cmd_account import AccountApp

logger = logging.getLogger(__name__)


class ApplabCli:
    def __init__(self, applab: Applab):
        app = App(name="applab")
        # cyclopts默认把--help和--version放在'Commands' group里，但这样不符合cli的习惯
        # Change the group of "--help" and "--version" to the implicitly created "Admin" group.
        app["--help"].group = "Cli info options"
        app["--version"].group = "Cli info options"
        app.default(self._root_cmd)
        app.command(AccountApp(applab).app, name="account")

        self.app = app
        self.applab = applab

    def _root_cmd(self):
        """
        One click install app on some cloud.

        ## Examples

        ```bash
        applab vendor list
        applab vendor info tencentcloud
        applab vendor login tencentcloud
        applab zone list --vendor tencentcloud
        applab install docker --vendor tencentcloud --zone ap-shanghai-1
        applab x docker install --vendor tencentcloud --zone ap-shanghai-1

        applab app list --vendor tencentcloud --zone ap-shanghai-1
        applab app list --vendor tencentcloud
        ```

        """
        # if help
        self.app.help_print()


def __setup_logging():
    """
    applab logging bootstrap

    需求：
    - CLI 业务输出走 stdout
    - logging 走 stderr
    - 应用可控，第三方库默认安静
    """

    # todo loglevel -v param
    log_level: str = os.getenv("APPLAB_LOG_LEVEL", "WARNING").upper()
    log_level: int = getattr(logging, log_level, logging.WARNING)
    logging.basicConfig(
        level=log_level,
        stream=sys.stderr,  # 不污染 stdout
        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(name)s: "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        # https://rich.readthedocs.io/en/stable/logging.html
        handlers=[RichHandler()],
    )

    # --- 第三方库降噪 ---
    log_level_deps = logging.WARNING
    logging.getLogger("urllib3").setLevel(log_level_deps)
    logging.getLogger("requests").setLevel(log_level_deps)
    logging.getLogger("botocore").setLevel(log_level_deps)
    logging.getLogger("boto3").setLevel(log_level_deps)


def main():
    __setup_logging()
    logger.info(f"applab started {__name__}")

    # app()
    version = "0.0.1"
    applab = Applab()
    applab.vendors.register(tencentcloud.TencentCloudVendor(version=version))
    applab.vendors.register(tencentcloud.AliyunVendor(version=version))

    ApplabCli(applab).app()


if __name__ == "__main__":
    main()
