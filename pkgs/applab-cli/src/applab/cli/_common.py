from typing import Any
from rich.console import Console
from typing import Dict, Literal
from rich.style import Style
from rich.theme import Theme

# 定义标准 M3 角色类型（Color Tokens）
M3_ROLE = Literal[
    # Primary
    "primary", "on_primary",
    "primary_container", "on_primary_container",

        # Secondary
    "secondary", "on_secondary",
    "secondary_container", "on_secondary_container",

        # Tertiary
    "tertiary", "on_tertiary",
    "tertiary_container", "on_tertiary_container",

        # Error
    "error", "on_error",
    "error_container", "on_error_container",

        # Surface system
    "surface", "on_surface",
    "surface_variant", "on_surface_variant",

        # Surface containers (elevation)
    "surface_container", "surface_container_high", "surface_container_low",

        # Inverse surfaces
    "inverse_surface", "on_inverse_surface",

        # Outline / divider
    "outline",

        # Shadow and scrim
    "scrim", "shadow"
]


class _Material3Colors:
    def __init__(self, *, dark: bool = True, high_contrast: bool = False):
        self.dark = dark
        self.high_contrast = high_contrast
        self.roles = self._build()

    def _build(self) -> Dict[M3_ROLE, str]:
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

                "tertiary": "#EFB8C8",
                "on_tertiary": "#492532",
                "tertiary_container": "#633B48",
                "on_tertiary_container": "#FFD8E4",

                "error": "#F2B8B5",
                "on_error": "#601410",
                "error_container": "#8C1D18",
                "on_error_container": "#F9DEDC",

                "surface": "#1C1B1F",
                "on_surface": "#E6E1E5" if not self.high_contrast else "#FFFFFF",
                "surface_variant": "#49454F",
                "on_surface_variant": "#CAC4D0",

                "surface_container": "#2B2930",
                "surface_container_high": "#36343B",
                "surface_container_low": "#211F26",

                "inverse_surface": "#FFFFFF" if not self.high_contrast else "#000000",
                "on_inverse_surface": "#000000" if not self.high_contrast else "#FFFFFF",

                "outline": "#938F99",

                "scrim": "#000060",  # 半透明黑色遮罩层
                "shadow": "#000040",  # 半透明黑色阴影
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

                "tertiary": "#7D5260",
                "on_tertiary": "#FFFFFF",
                "tertiary_container": "#FFD8E4",
                "on_tertiary_container": "#31111D",

                "error": "#B3261E",
                "on_error": "#FFFFFF",
                "error_container": "#F9DEDC",
                "on_error_container": "#410E0B",

                "surface": "#FFFBFE",
                "on_surface": "#1C1B1F",
                "surface_variant": "#E7E0EB",
                "on_surface_variant": "#49454F",

                "surface_container": "#F3EDF7",
                "surface_container_high": "#ECE6F0",
                "surface_container_low": "#F7F2FA",

                "inverse_surface": "#1C1B1F",
                "on_inverse_surface": "#FFFFFF",

                "outline": "#79747E",

                "scrim": "#000060",  # 半透明黑色遮罩层
                "shadow": "#000040",  # 半透明黑色阴影
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

            # Tertiary
            "tertiary": Style(color=c["on_tertiary"], bgcolor=c["tertiary"]),
            "tertiary.container": Style(
                color=c["on_tertiary_container"], bgcolor=c["tertiary_container"]
            ),

            # Error
            "error": Style(color=c["on_error"], bgcolor=c["error"]),
            "error.container": Style(
                color=c["on_error_container"], bgcolor=c["error_container"]
            ),

            # Surfaces
            "surface": Style(color=c["on_surface"], bgcolor=c["surface"]),
            "surface.variant": Style(
                color=c["on_surface_variant"], bgcolor=c["surface_variant"]
            ),

            # Surface containers (elevation)
            "surface.container": Style(
                color=c["on_surface"], bgcolor=c["surface_container"]
            ),
            "surface.container.high": Style(
                color=c["on_surface"], bgcolor=c["surface_container_high"]
            ),
            "surface.container.low": Style(
                color=c["on_surface"], bgcolor=c["surface_container_low"]
            ),

            # Inverse surfaces
            "inverse_surface": Style(color=c["on_inverse_surface"], bgcolor=c["inverse_surface"]),

            # Outline / divider
            "outline": Style(color=c["outline"]),

            # Shadow and scrim
            "scrim": Style(color=c["scrim"], bgcolor=c["scrim"]),
            "shadow": Style(color=c["shadow"], bgcolor=c["shadow"]),
        })


UXSemantic = Literal["success", "warning", "info", "error", "input"]

# 默认映射值，作为对象初始化的默认参数
_DEFAULT_MAP: Dict[UXSemantic, str] = {
    # No semantic color in M3 → mapped roles
    "success": "primary",
    "warning": "tertiary",
    "info": "surface_variant",
    # The only true semantic color in M3
    "error": "error",
    "input": "surface",
}

_DEFAULT_PREFIX: Dict[UXSemantic, str] = {
    "success": "[OK]",
    "warning": "[WARN]",
    "info": "[INFO]",
    "error": "[ERROR]",
    "input": "[*]",
}


class UXSemanticMapper:
    """
    Maps UX semantics to Material 3 color roles.

    This is a policy, NOT a design system.
    """

    def __init__(self,
                 map_: Dict[UXSemantic, str] | None = None,
                 prefix: Dict[UXSemantic, str] | None = None):
        """
        初始化UXSemanticMapper实例

        Args:
            map_: UX语义到M3颜色角色的映射字典（默认为DEFAULT_MAP）
            prefix: UX语义到前缀的映射字典（默认为DEFAULT_PREFIX）
        """
        self.map = map_ or _DEFAULT_MAP
        self.prefix = prefix or _DEFAULT_PREFIX

    def style_for(self, semantic: UXSemantic) -> str:
        """
        根据UX语义返回对应的M3颜色角色

        Args:
            semantic: UX语义类型

        Returns:
            对应的M3颜色角色字符串
        """
        return self.map[semantic]

    def prefix_for(self, semantic: UXSemantic) -> str:
        """
        根据UX语义返回对应的前缀

        Args:
            semantic: UX语义类型

        Returns:
            对应的前缀字符串
        """
        return self.prefix[semantic]


class Cli:
    def __init__(self) -> None:
        theme = _Material3Colors(dark=True, high_contrast=False).to_rich_theme()
        self.console = Console(theme=theme, color_system="standard")
        self.console_err = Console(stderr=True, theme=theme)
        self.uxSemantic = UXSemanticMapper()

    def print(self, *objects: Any) -> None:
        self.console.print(*objects)

    def error(self, *objects: Any) -> None:
        self.console_err.print(self.uxSemantic.prefix_for("error"), *objects)

    def info(self, *objects: Any) -> None:
        self.console.print(self.uxSemantic.prefix_for("info"), *objects)

    def success(self, *objects: Any) -> None:
        self.console.print(self.uxSemantic.prefix_for("success"), *objects)

    def warning(self, *objects: Any) -> None:
        self.console.print(self.uxSemantic.prefix_for("warning"), *objects)


cli = Cli()

if __name__ == "__main__":
    cli.print("[primary]INSTALL[/]")
    cli.print("[primary.container]INSTALL[/]")

    cli.print("[surface.container.high]Created at 2025-01-01[/]")
    cli.print("[error]Failed[/]")
    cli.print("[surface.container.low] Cluster Ready [/]")

    cli.print("[tertiary]This is tertiary color[/]")
    cli.print("[tertiary.container]This is tertiary container color[/]")

    cli.print("[inverse_surface]This is inverse surface[/]")
    cli.print("[scrim]This is a scrim overlay[/]")
    cli.print("[shadow]This is shadow[/]")
