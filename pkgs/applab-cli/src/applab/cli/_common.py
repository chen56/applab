from typing import Any

from rich.console import Console
from typing import Dict, Literal
from rich.style import Style
from rich.theme import Theme

_M3_ROLE = Literal[
    # Primary
    "primary", "on_primary",
    "primary_container", "on_primary_container",

        # Secondary
    "secondary", "on_secondary",
    "secondary_container", "on_secondary_container",

        # Error
    "error", "on_error",
    "error_container", "on_error_container",

        # Surface system
    "background", "on_background",
    "surface", "on_surface",
    "surface_variant", "on_surface_variant",

        # Surface containers (elevation)
    "surface_container_low",
    "surface_container",
    "surface_container_high",

        # Outline
    "outline",
]


class _Material3Colors:
    def __init__(self, *, dark: bool = True, high_contrast: bool = False):
        self.dark = dark
        self.high_contrast = high_contrast
        self.roles = self._build()

    def _build(self) -> Dict[_M3_ROLE, str]:
        if self.dark:
            return {
                "primary": "#D0BCFF" if not self.high_contrast else "#F3EDFF",
                "on_primary": "#381E72",
                "primary_container": "#4F378B",
                "on_primary_container": "#EADDFF",

                "secondary": "#CCC2DC",
                "on_secondary": "#332D41",
                "secondary_container": "#4A4458",
                "on_secondary_container": "#E8DEF8",

                "error": "#F2B8B5",
                "on_error": "#601410",
                "error_container": "#8C1D18",
                "on_error_container": "#F9DEDC",

                "background": "#1C1B1F",
                "on_background": "#E6E1E5",

                "surface": "#1C1B1F",
                "on_surface": "#E6E1E5" if not self.high_contrast else "#FFFFFF",
                "surface_variant": "#49454F",
                "on_surface_variant": "#CAC4D0",

                "surface_container_low": "#211F26",
                "surface_container": "#2B2930",
                "surface_container_high": "#36343B",

                "outline": "#938F99",
            }
        else:
            return {
                "primary": "#6750A4",
                "on_primary": "#FFFFFF",
                "primary_container": "#EADDFF",
                "on_primary_container": "#21005D",

                "secondary": "#625B71",
                "on_secondary": "#FFFFFF",
                "secondary_container": "#E8DEF8",
                "on_secondary_container": "#1D192B",

                "error": "#B3261E",
                "on_error": "#FFFFFF",
                "error_container": "#F9DEDC",
                "on_error_container": "#410E0B",

                "background": "#FFFBFE",
                "on_background": "#1C1B1F",

                "surface": "#FFFBFE",
                "on_surface": "#1C1B1F",
                "surface_variant": "#E7E0EB",
                "on_surface_variant": "#49454F",

                "surface_container_low": "#F7F2FA",
                "surface_container": "#F3EDF7",
                "surface_container_high": "#ECE6F0",

                "outline": "#79747E",
            }

    def to_rich_theme(self) -> Theme:
        c = self.roles
        return Theme({
            # Primary / Secondary actions
            "primary": Style(color=c["on_primary"], bgcolor=c["primary"]),
            "primary.container": Style(
                color=c["on_primary_container"], bgcolor=c["primary_container"]
            ),

            "secondary": Style(color=c["on_secondary"], bgcolor=c["secondary"]),
            "secondary.container": Style(
                color=c["on_secondary_container"], bgcolor=c["secondary_container"]
            ),

            # Error
            "error": Style(color=c["on_error"], bgcolor=c["error"]),
            "error.container": Style(
                color=c["on_error_container"], bgcolor=c["error_container"]
            ),

            # Surfaces
            "background": Style(color=c["on_background"], bgcolor=c["background"]),
            "surface": Style(color=c["on_surface"], bgcolor=c["surface"]),
            "surface.variant": Style(
                color=c["on_surface_variant"], bgcolor=c["surface_variant"]
            ),
            "surface.low": Style(
                color=c["on_surface"], bgcolor=c["surface_container_low"]
            ),
            "surface.high": Style(
                color=c["on_surface"], bgcolor=c["surface_container_high"]
            ),

            # Outline / divider
            "outline": Style(color=c["outline"]),
        })


class Cli:
    def __init__(self):
        theme = _Material3Colors(dark=True, high_contrast=False).to_rich_theme()
        self.console = Console(theme=theme)
        self.console_err = Console(stderr=True, theme=theme)

    def print(self, *objects: Any):
        self.console.print(*objects)

    def print_err(self, *objects: Any):
        self.console_err.print(*objects)


cli = Cli()

if __name__ == "__main__":
    cli.print("[primary]INSTALL[/]")
    cli.print("[primary.container]INSTALL[/]")

    cli.print("[surface.high]Created at 2025-01-01[/]")
    cli.print("[error]Failed[/]")
    cli.print("[surface.low] Cluster Ready [/]")
