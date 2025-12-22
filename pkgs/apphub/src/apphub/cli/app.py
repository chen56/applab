from cyclopts import App
from .provider import provider_app



app = App()

# Change the group of "--help" and "--version" to the implicitly created "Admin" group.
app["--help"].group = "Cli info options"
app["--version"].group = "Cli info options"


# Child app inherits parent's settings
provider_app = app.command(provider_app, "provider")



@app.default()
def main():
    """
    One click install app on some cloud.

    ```bash
    apphub provider list
    apphub provider info qcloud
    apphub provider login qcloud
    apphub zone list --provider qcloud
    apphub install docker --provider qcloud --zone ap-shanghai-1
    apphub x docker install --provider qcloud --zone ap-shanghai-1

    apphub app list --provider qcloud --zone ap-shanghai-1
    apphub app list --provider qcloud
    ```

    """
    # if help
    app.help_print()
app()
if __name__ == "__main__":
    provider_app()