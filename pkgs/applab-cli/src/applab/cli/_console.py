"""

# Console

## 定位

- Console是cli的业务信息输入/输出工具, 并不是日志，日志应使用logging
- 用来封装替换print/rich的， print太简单,rich有点小复杂暂时不直接用
- 为rich增强了 Material 3 Color Roles

┌────────────────────────────┐
│ CLI UX Layer               │  ← print / rich / click.echo -> 本模块Console
│（用户可见、稳定）             │
├────────────────────────────┤
│ Business Events            │  ← logger.info / warning
│（结构化、可观测）             │
├────────────────────────────┤
│ Debug / Diagnostics        │  ← logger.debug
├────────────────────────────┤
│ System Errors              │  ← logger.error / exception
└────────────────────────────┘


| 内容           | 去向              |
| ------------ | ----------------- |
| 命令返回值 / JSON | stdout            |
| 用户友好提示       | stdout            |
| 进度 / 状态说明    | stderr 或 TTY-only |
| 调试 / 诊断      | logging           |




## Material 3 颜色系统：

Layer 1: Material 3 Color Roles（官方，不能改）
  - primary / on_surface / on_surface_variant / outline ...

Layer 2: Layer 2: Rich Theme (M3 Colors to Rich CLI)
  - 这一层将 M3 色彩角色映射到 Rich CLI 的 Style(color=..., bgcolor=...)
  - 严格选用Material 3的词汇，不扩展语义，只组合背景、前景色为主要style元素，名字也是第一层的名字（主要是背景名）

Layer 3: Business Semantic Mapping
  - 这一层为业务语义函数（如 info(), warn(), success(), error() 等），映射为第二层或第一层，加上特定的前缀或后缀来进行风格化处理。

应用代码主要以使用Layer 3函数为主，无法表达时，可用Layer 2表达，而Layer 1只是颜色表，无法直接使用。


"""

from typing import Any, Dict, Literal, cast

from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.theme import Theme

# 定义标准 M3 角色类型（Color Tokens）
_Material3_Color_Role_Name = Literal[
    # Primary
    "primary",
    "on_primary",
    "primary_container",
    "on_primary_container",
        # Secondary
    "secondary",
    "on_secondary",
    "secondary_container",
    "on_secondary_container",
        # Tertiary
    "tertiary",
    "on_tertiary",
    "tertiary_container",
    "on_tertiary_container",
        # Error
    "error",
    "on_error",
    "error_container",
    "on_error_container",
        # Surface system
    "surface",
    "on_surface",
    "surface_variant",
    "on_surface_variant",
        # Surface containers (elevation)
    "surface_container",
    "surface_container_high",
    "surface_container_low",
        # Inverse surfaces
    "inverse_surface",
    "on_inverse_surface",
        # Outline / divider
    "outline",
        # Shadow and scrim
    "scrim",
    "shadow",
]

_RichStyleName = Literal[
    "primary",
    "primary_container",
    "secondary",
    "secondary_container",
    "tertiary",
    "tertiary_container",
    "error",
    "error_container",
    "surface",
    "surface_variant",
    "surface_container",
    "surface_container_high",
    "surface_container_low",
    "inverse_surface",
    "outline",
    "scrim",
    "shadow",
]


def _build_material3_color_roles(*, dark: bool) -> Dict[_Material3_Color_Role_Name, str]:
    if dark:
        return {
            # Primary (主色)
            "primary": "#2979FF",  # 蓝色 #2979FF (Vibrant Blue)
            "on_primary": "#FFFFFF",  # 白色 (On Primary: text/foreground on primary background)
            "primary_container": "#1565C0",  # 深蓝色 #1565C0 (Deep Blue)
            "on_primary_container": "#FFFFFF",  # 白色 (On Primary Container)
            # Secondary (次要色)
            "secondary": "#80D6FF",  # 浅蓝色 #80D6FF (Light Blue)
            "on_secondary": "#003C8F",  # 深蓝色 (On Secondary: text on secondary background)
            "secondary_container": "#1E88E5",  # 深蓝色 #1E88E5 (Dark Blue)
            "on_secondary_container": "#FFFFFF",  # 白色 (On Secondary Container)
            # Tertiary (第三色)
            "tertiary": "#64B5F6",  # 淡蓝色 #64B5F6 (Soft Blue)
            "on_tertiary": "#FFFFFF",  # 白色 (On Tertiary: text on tertiary background)
            "tertiary_container": "#1E3C8F",  # 暗蓝色 #1E3C8F (Dark Blue)
            "on_tertiary_container": "#FFD8E4",  # 粉色 #FFD8E4 (Soft Pink)
            # Error (错误色)
            "error": "#FF3B30",  # 错误红色 #FF3B30 (Red)
            "on_error": "#FFFFFF",  # 白色 (On Error: text on error background)
            "error_container": "#F1C2C0",  # 淡红色 #F1C2C0 (Light Red)
            "on_error_container": "#601410",  # 深红色 #601410 (Dark Red)
            # Surface (背景色)
            "surface": "#121212",  # 深灰 #121212 (Deep Grey)
            "on_surface": "#E6E1E5",  # 白色 (On Surface: text on surface)
            "surface_variant": "#49454F",  # 深灰紫 #49454F (Greyish Purple)
            "on_surface_variant": "#CAC4D0",  # 淡灰色 #CAC4D0 (Light Grey)
            # Surface Containers (容器背景)
            "surface_container": "#2B2930",  # 深灰色 #2B2930 (Dark Grey)
            "surface_container_high": "#36343B",  # 更深灰色 #36343B (Darker Grey)
            "surface_container_low": "#211F26",  # 深棕色 #211F26 (Deep Brown)
            # Inverse Surface (反转背景)
            "inverse_surface": "#FFFFFF",  # 白色 (Inverse Surface: 白色背景)
            "on_inverse_surface": "#000000",  # 黑色 (On Inverse Surface: 黑色文字)
            # Outline (轮廓)
            "outline": "#B3B3B3",  # 浅灰 #B3B3B3 (Light Grey Outline)
            # Scrim & Shadow (遮罩与阴影)
            "scrim": "#000080",  # 半透明黑色遮罩层
            "shadow": "#000060",  # 半透明黑色阴影
        }
    else:
        return {
            # Primary (主色)
            "primary": "#2979FF",  # 蓝色 #2979FF (Vibrant Blue)
            "on_primary": "#FFFFFF",  # 白色 (On Primary: text/foreground on primary background)
            "primary_container": "#1565C0",  # 深蓝色 #1565C0 (Deep Blue)
            "on_primary_container": "#FFFFFF",  # 白色 (On Primary Container)
            # Secondary (次要色)
            "secondary": "#80D6FF",  # 浅蓝色 #80D6FF (Light Blue)
            "on_secondary": "#003C8F",  # 深蓝色 (On Secondary: text on secondary background)
            "secondary_container": "#1E88E5",  # 深蓝色 #1E88E5 (Dark Blue)
            "on_secondary_container": "#FFFFFF",  # 白色 (On Secondary Container)
            # Tertiary (第三色)
            "tertiary": "#64B5F6",  # 淡蓝色 #64B5F6 (Soft Blue)
            "on_tertiary": "#FFFFFF",  # 白色 (On Tertiary: text on tertiary background)
            "tertiary_container": "#1E3C8F",  # 暗蓝色 #1E3C8F (Dark Blue)
            "on_tertiary_container": "#FFD8E4",  # 粉色 #FFD8E4 (Soft Pink)
            # Error (错误色)
            "error": "#FF3B30",  # 错误红色 #FF3B30 (Red)
            "on_error": "#FFFFFF",  # 白色 (On Error: text on error background)
            "error_container": "#F1C2C0",  # 淡红色 #F1C2C0 (Light Red)
            "on_error_container": "#601410",  # 深红色 #601410 (Dark Red)
            # Surface (背景色)
            "surface": "#FFFBFE",  # 浅灰色 #FFFBFE (Light Grey)
            "on_surface": "#1C1B1F",  # 深灰色 #1C1B1F (On Surface: text on surface)
            "surface_variant": "#E7E0EB",  # 浅紫灰色 #E7E0EB (Light Purple Grey)
            "on_surface_variant": "#49454F",  # 深灰紫 #49454F (Dark Grey Purple)
            # Surface Containers (容器背景)
            "surface_container": "#F3EDF7",  # 浅紫色 #F3EDF7 (Light Purple)
            "surface_container_high": "#ECE6F0",  # 更浅紫色 #ECE6F0 (Lighter Purple)
            "surface_container_low": "#F7F2FA",  # 浅灰紫色 #F7F2FA (Light Grey Purple)
            # Inverse Surface (反转背景)
            "inverse_surface": "#1C1B1F",  # 黑色 (Inverse Surface: 黑色背景)
            "on_inverse_surface": "#FFFFFF",  # 白色 (On Inverse Surface: 白色文字)
            # Outline (轮廓)
            "outline": "#79747E",  # 深灰 #79747E (Deep Grey Outline)
            # Scrim & Shadow (遮罩与阴影)
            "scrim": "#000080",  # 半透明黑色遮罩层 #00000080 (Semi-transparent Black)
            "shadow": "#000060",  # 半透明阴影 #00000060 (Semi-transparent Shadow)
        }


def _to_rich_theme(*, roles) -> Theme:
    c = roles
    styles: Dict[_RichStyleName, Style] = {
        "primary": Style(color=c["on_primary"], bgcolor=c["primary"]),
        "primary_container": Style(color=c["on_primary_container"], bgcolor=c["primary_container"]),
        "secondary": Style(color=c["on_secondary"], bgcolor=c["secondary"]),
        "secondary_container": Style(color=c["on_secondary_container"], bgcolor=c["secondary_container"]),
        "tertiary": Style(color=c["on_tertiary"], bgcolor=c["tertiary"]),
        "tertiary_container": Style(color=c["on_tertiary_container"], bgcolor=c["tertiary_container"]),
        "error": Style(color=c["on_error"], bgcolor=c["error"]),
        "error_container": Style(color=c["on_error_container"], bgcolor=c["error_container"]),
        "surface": Style(color=c["on_surface"], bgcolor=c["surface"]),
        "surface_variant": Style(color=c["on_surface_variant"], bgcolor=c["surface_variant"]),
        "surface_container_low": Style(color=c["on_surface"], bgcolor=c["surface_container_low"]),
        "surface_container": Style(color=c["on_surface"], bgcolor=c["surface_container"]),
        "surface_container_high": Style(color=c["on_surface"], bgcolor=c["surface_container_high"]),
        "inverse_surface": Style(color=c["on_inverse_surface"], bgcolor=c["inverse_surface"]),
        "outline": Style(color=c["outline"]),
        "scrim": Style(bgcolor=c["scrim"]),
        "shadow": Style(bgcolor=c["shadow"]),
    }
    return Theme(styles=cast(Dict[str, Style], styles))


class _Console:
    """
    all cli info/error/waring output to stdout, its app logic, not log.
    """

    def __init__(self, *, dark: bool = False):
        # Layer 1 Material 3 Color Roles
        m3_color_roles: dict[_Material3_Color_Role_Name, str] = _build_material3_color_roles(dark=dark)
        # Layer 2: Rich Theme (M3 Colors to Rich CLI)
        self._rich_theme = _to_rich_theme(roles=m3_color_roles)

        # Layer 3: Business Semantic Mapping : success()/info() function
        self.console = Console(theme=self._rich_theme, color_system="truecolor")

    def rich_style(self, name: _RichStyleName) -> Style:
        return self._rich_theme.styles[name]

    def print(self, *objects: Any) -> None:
        self.console.print(*objects)

    def markdown(self, markup: str) -> None:
        self.console.print(Markdown(markup))

    def success(self, *objects: Any) -> None:
        self._print("🟢", *objects, style="primary")

    def warn(self, *objects: Any) -> None:
        self._print(":warning-emoji:", *objects, style="tertiary")

    def info(self, *objects: Any) -> None:
        self._print("ℹ️", *objects, style="surface_variant")

    def input(self, *objects: Any) -> None:
        self._print("🧷", *objects, style="surface")

    def error(self, *objects: Any) -> None:
        self._print("🔴", *objects, style="error")

    def _print(self, *objects: Any, style: _RichStyleName):
        self.console.print(*objects, style=self.rich_style(style))


console = _Console()

if __name__ == "__main__":
    console.print("## 颜色系统Layer 2 层使用范例")
    console.print("[primary]primary[/]")
    console.print("[primary_container]primary_container[/]")

    console.print("[secondary]secondary[/]")
    console.print("[secondary_container]secondary_container[/]")

    console.print("[tertiary]tertiary[/]")
    console.print("[tertiary_container]tertiary_container[/]")

    console.print("[error]error[/]")
    console.print("[error_container]error_container[/]")

    console.print("[surface]surface[/]")
    console.print("[surface_variant]surface_variant[/]")

    console.print("[surface_container]surface_container[/]")
    console.print("[surface_container_high]surface_container_high[/]")
    console.print("[surface_container_low]surface_container_low[/]")

    console.print("[inverse_surface]inverse_surface[/]")

    console.print("[outline]outline[/]")
    console.print("[scrim]scrim[/]")
    console.print("[shadow]shadow[/]")

    console.print("## 颜色系统Layer 3 层使用范例")
    console.success("This is success message. 一般情况下，内部无需指定格式语义，又第三层特殊函数自己处理")
    console.warn("This is warn message. 一般情况下，内部无需指定格式语义，又第三层特殊函数自己处理")
    console.info("This is info message. 一般情况下，内部无需指定格式语义，又第三层特殊函数自己处理")
    console.input("This is input message. 一般情况下，内部无需指定格式语义，又第三层特殊函数自己处理")
    console.error("This is error message. 一般情况下，内部无需指定格式语义，又第三层特殊函数自己处理")
