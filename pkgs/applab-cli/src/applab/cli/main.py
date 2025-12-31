"""cli main入口"""

from cyclopts import App

from .vendor import account_app

app = App(name="applab")

# cyclopts默认把--help和--version放在'Commands' group里，但这样不符合cli的习惯
# Change the group of "--help" and "--version" to the implicitly created "Admin" group.
app["--help"].group = "Cli info options"
app["--version"].group = "Cli info options"

# Child app inherits parent's settings
account_app = app.command(account_app, "vendor", alias="p")


@app.default()
def _root_cmd():
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
    app.help_print()


def main():
    app()


#
if __name__ == "__main__":
    main()
