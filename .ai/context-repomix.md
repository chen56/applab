This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.py, **/*.md, **/*.toml, **/.gitignore, **/*.bash
- Files matching these patterns are excluded: .ai/**, pkgs/**/sha.bash, pkgs/**/README.md, .trae/**, .vscode/**, .idea/**, **/tests/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  dev-core.md
  dev.md
  README.md
pkgs/
  applab-cli/
    src/
      applab/
        cli/
          __init__.py
          _cmd_account.py
          _console.py
          main.py
    pyproject.toml
  applab-core/
    src/
      applab/
        core/
          __init__.py
          _account.py
          _base.py
          _constant.py
          _param_model.py
          asserts.py
          error.py
          storage.py
    pyproject.toml
  applab-vendor-tencentcloud/
    src/
      applab/
        vendor/
          tencentcloud/
            __init__.py
            aliyun.py
            tendentcloud.py
    pyproject.toml
src/
  applab/
    README.md
.gitignore
pyproject.toml
README.md
sha_common.bash
sha.bash
shab.bash
```

# Files

## File: docs/dev.md
````markdown
# 开发

## 项目初始化

## 已采纳

- 验证及模型定义: [pydantic](https://pydantic.dev)
- 日志:
- 命令cli: [cyclopts](https://github.com/BrianPugh/cyclopts)
- py项目管理/build: [uv](https://github.com/astral-sh/uv)
- 类型注解
  - 类型注解元数据: [annotated-types](https://github.com/annotated-types/annotated-types)
    - Python 3.9+ 引入的 typing.Annotated 仅支持「类型 + 任意元数据」的基础形式（如 Annotated[int, "positive"]）；而 annotated_types 则提供了标准化、可复用的元数据类，让类型注解的约束更清晰、可机器解析（比如被 Pydantic、FastAPI 等库识别）。

## 依赖候选

### 可观测性

- https://github.com/pydantic/logfire
````

## File: pkgs/applab-core/src/applab/core/asserts.py
````python
from deepdiff import DeepDiff
from deepdiff.helper import COLORED_VIEW


def __get_all_paths(d, current_path="root"):
    """get all paths from a nested dict or list"""
    paths = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_path = f"{current_path}['{k}']"
            paths.extend(__get_all_paths(v, new_path))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_path = f"{current_path}[{i}]"
            paths.extend(__get_all_paths(v, new_path))
    else:
        # leaf node（int, str, float...）
        paths.append(current_path)
    return paths


def diff_subset(expected_subset: dict, fullset: dict, ):
    diff = DeepDiff(fullset, expected_subset, include_paths=__get_all_paths(expected_subset), view=COLORED_VIEW)
    assert {} == diff, diff
````

## File: pkgs/applab-core/src/applab/core/error.py
````python
"""

AppError
│
├── CheckError
│   └─ Invariant / assumption violated
│   （替代assert的断言/不变量检查，bug, 程序问题）
│
├── BizError
│   ├─ NotLoggedIn
│   ├─ PermissionDenied
│   ├─ QuotaExceeded
│   └─ InvalidWorkflow
│   （业务规则 / 流程失败, 用户操作/状态问题）
│
└── 未分类其他异常
    ├─ NetworkDisconnected
    └─ DeviceUnavailable
    （究竟是系统问题还是什么问题需要程序边界解释器自行动态解释）

"""


# reference:
# https://docs.python.org/zh-cn/3.14/library/exceptions.html
# https://docs.python.org/zh-cn/3.14/tutorial/errors.html
class ApplabError(Exception):
    """Base class for all application-level errors."""

    user_visible: bool = False
    retryable: bool = False


# ---------- Business ----------


class BizError(ApplabError):
    """
    业务异常: 可预料的业务流程，非故障，比如:
    - 用户可感知错误: 表单、权限、操作超限
    - 业务流程异常: 状态机异常、业务规则冲突

    处理事项：
    - 应用于 CLI/GUI 的提示
    - 不应打印 traceback 到终端
    - 可携带结构化信息（字段名、错误码）
    """

    pass


# ---------- Check / Invariant ----------


class CheckError(AssertionError):
    """
    Invariant Check Error, like `assert`, but assert not raise error when running in optimized mode

    ref: <https://discuss.python.org/t/stop-ignoring-asserts-when-running-in-optimized-mode>
    """

    user_visible = False
    retryable = False


def check(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)
````

## File: pkgs/applab-core/src/applab/core/storage.py
````python
import os
import pathlib
from pathlib import Path

from pydantic import BaseModel


class JsonStorage[T: BaseModel]:
    def __init__(self, path: Path, model: type[T]):
        self.path = path
        self.model = model

    def load(self) -> T:
        if not self.path.exists():
            # 要求无参构造器
            return self.model()

        json_string = pathlib.Path(self.path).read_text(encoding="utf-8")
        return self.model.model_validate_json(json_string)

    def save(self, doc: T):
        atomic_save_text(self.path, doc.model_dump_json(indent=4))


# ---------------------------
# 文本版本
# ---------------------------
def atomic_save_text(
        path: Path,
        text: str,
        *,
        encoding: str = "utf-8",
        fsync: bool = True,
) -> None:
    """
    Atomically save text or JSON-serializable data to a file.

    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = _temp_file_path(path)

    with open(tmp, "w", encoding=encoding) as f:
        f.write(text)
        f.flush()
        if fsync:
            os.fsync(f.fileno())

    os.replace(tmp, path)


# ---------------------------
# 二进制版本
# ---------------------------
def atomic_save_bytes(
        path: Path,
        data: bytes,
        *,
        fsync: bool = True,
) -> None:
    """
    Atomically save binary data to a file.
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = _temp_file_path(path)

    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        if fsync:
            os.fsync(f.fileno())

    os.replace(tmp, path)


def _temp_file_path(path: Path) -> Path:
    """
    注意：
    1. 未使用tempfile.NamedTemporaryFile工具,因为它默认目录为/var/folders/.../T/tmpxxxx，而path可能在云盘，
    跨文件系统的os.replace不是原子操作。
    2. tmp文件即便失败也不用清理，下次重新覆盖和os.replace
    """
    return path.with_name(f".{path.name}.tmp")
````

## File: pkgs/applab-core/src/applab/core/_param_model.py
````python
from pydantic import BaseModel


class BaseParamModel(BaseModel):
    model_config = {"kw_only": True}


class UIField(BaseModel):
    model_config = {"kw_only": True}  # 强制所有字段为关键字参数


class TextField(UIField):
    label: str
    # error:Fields with a default value must come after any fields without a default.
    type: str
    help: str = ""
````

## File: README.md
````markdown
# pq

## 代码约定

遵循提交规范: <https://www.conventionalcommits.org/zh-hans/v1.0.0/>
````

## File: sha_common.bash
````bash
#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略 xxx 函数未被使用的警告

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

# On Mac OS, readlink -f doesn't work, so use._real_path get the real path of the file
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)


_print_info() {
  echo -e "\e[44;37m$1\e[0m"
}
_print_error() {
  echo -e "\e[44;37m$1\e[0m"
}


# color text : ref: https://m3.material.io/styles/color
#_text "success"   "Cloud resource created successfully."
#_text "error"     "Failed to connect to AWS instance."
#_text "warning"   "High cost alert: Instance is running on high-spec."
#_text "info"      "Deploying AI model to cluster..."
#_text "primary"   "AppHub is ready for configuration."
#_text "secondary" "Processing background tasks..."
#_text "tertiary"   "current workspace: $ROOT_DIR"
#_text "neutral"   "Help to email support@applab."
_text() {
    local type="$1"
    shift
    local text="$*"

    local type_lower=$(echo "$type" | tr '[:upper:]' '[:lower:]')
    local type_upper=$(echo "$type" | tr '[:lower:]' '[:upper:]')

    case "$type_lower" in
        "success")   color_code="38;5;255;48;5;28;1"  ;; # 森林绿
        "error")     color_code="38;5;255;48;5;124;1" ;; # 砖红
        "warning")   color_code="38;5;16;48;5;214;1"  ;; # 琥珀黄 (黑字)
        "info")      color_code="38;5;255;48;5;31;1"  ;; # 钢蓝
        "primary")   color_code="38;5;255;48;5;55;1"  ;; # 深紫 (M3 Primary)
        "secondary") color_code="38;5;255;48;5;66;1"  ;; # 灰青 (M3 Secondary)
        "tertiary")  color_code="38;5;255;48;5;23;1"  ;; # 深青 (M3 Tertiary - Deep Teal)
        "neutral")   color_code="38;5;255;48;5;243;1" ;; # 中灰
        *)           color_code="38;5;255;48;5;243;1" ;; # 默认
    esac
    printf "\033[%sm%s\033[0m" "$color_code" "$text"
}

# 清晰的函数调用日志，替代 `set -x` 功能
#
# Usage:   _run <some cmd>
# Example: _run docker compose up
#
# 假设你的./sake 脚本里有个函数：
# up() {
#   _run docker compose up;  # ./sake 的 22行
# }
# 运行`./sake up`后打印日志：
# 🔵 ./sake:22 up() ▶︎【/home/ubuntu/current_work_dir$ docker compose up】
# 你可以清晰的看到:
#   - 在脚本的哪一行: ./sake:22
#   - 哪个函数: up()
#   - 在哪个工作目录: /home/ubuntu/current_work_dir
#   - 执行了什么: docker compose up
# 在vscode中，按住macbook的cmd键,点终端上输出的‘./sake:106’, 可以让编辑器跳转到对应的脚本行，很方便
# 获取调用栈的原理：
#   `caller 0`输出为`22 foo ./sake`，即调用_run函数的调用栈信息：行号、函数,脚本
_run() {
  local caller_script=$(caller 0 | awk '{print $3}')
    # shellcheck disable=SC2001
  local caller_script=$(echo "$caller_script" | sed "s@^$HOME@~@" )

  local caller_line=$(caller 0 | awk '{print $1}')
  # 把 /home/ubuntu/current_work_dir 替换为 ~/current_work_dir 短格式
  # 使用 @ 作为分隔符，避免与路径中的 / 冲突
  # shellcheck disable=SC2001
  local show_pwd=$(echo "$PWD" | sed "s@^$HOME@~@" )
  local color_caller=$(_text secondary "$caller_script:$caller_line ${FUNCNAME[1]}() ")
  local color_pwd=$(_text info "$show_pwd$ " )
  local color_cmd=$(_text primary "$*")
  echo "$color_caller$color_pwd$color_cmd" >&2
  "$@"
}

_install_sha() {
  _run mkdir -p "$ROOT_DIR/vendor"
  _run curl -L -o "$ROOT_DIR/vendor/sha.bash" https://github.com/chen56/sha/raw/main/sha.bash
}

if ! [[ -f "$ROOT_DIR/vendor/sha.bash" ]]; then
  _install_sha
fi

# shellcheck source=../vendor/sha.bash
source "$ROOT_DIR/vendor/sha.bash"

##################################################
# 每个项目的公共命令集
##################################################

self() {
  info() {
    echo "本项目使用的命令框架：https://github.com/chen56/sha"
  }
  upgrade() {
    _install_sha
  }
}

clean() (
  _run rm -rf .venv
  _run rm -rf .quarto
  _run rm -rf .ruff_cache
  _run rm -rf ./**/build
  _run rm -rf ./**/__pycache__
  _run rm -rf ./**/dist
  _run rm -rf ./**/*.egg-info
  _run rm -rf .pytest_cache
)
````

## File: docs/dev-core.md
````markdown
# cli 设计

## 概念设计

目前只记录可能的概念，不是实现要求

- vendor
    - Capabilities & Labels 能力
        - [cpu_vm, gpu_vm, k8s, cfs, dns]
    - vm
        - cpu: "2"
        - memory: "16GiB"
        - gpu: {type: "T4", count: 1}
- app app+核心计算存储单元，App + Variant + Resource Requirements<br />预定义脚本只暴露参数
    - meta
    - spec
        - name
        - version
        - variant/profiles 变体/配置方案，集群(HA/Cluster)部署、单机部署等，目前不确定是否真的需要?
        - feature 软件功能开关，比如开dns，开隧道，绑域名
        - requirements 平台需求
            - gpu: {type: "T4", count: 1}
            - memory: {min: "2Gi",max: "16Gi"}
            - network: {min: "10M",max: "100M"}
            - storage：{min: "10Gi",max: "100Gi"}
            - topology
                - mode: "cluster"
                - min_nodes: 3
            - vendor:
                - prefer: ["tencentcloud", "aws"]
                - require: {include: ["tencentcloud", "aws","aliyun"]} #特殊app要求部署特殊云厂商
            - os: Linux / Windows / macOS，glibc/musl
            - affinity: 暂时无
        - input param app可调整的参数
    - state(output)
- feature 软件功能/服务，配合app核心计算存储的外围服务，隧道、域名绑定等
    - dns
    - tunnel
    - 自动重启,因为会尽量使用便宜的竞价实例，需要有自动重建恢复机制
- deployment
    - runtime 运行时，app部署的目标可以切换，类似colab在cpu/gpu间切，省钱
        - region 国内外需要区分，因为有些mirror不同

### cli 

```bash
applab account login tencentcloud
applab account list
applab account info tencentcloud
applab zone list --vendor tencentcloud
applab app install docker --vendor tencentcloud --zone ap-shanghai-1
applab app list --vendor tencentcloud --zone ap-shanghai-1
applab app list --vendor tencentcloud
````

## File: pkgs/applab-core/src/applab/core/_constant.py
````python
from pathlib import Path
from typing import NamedTuple


class APPLAB(NamedTuple):
    APP_NAME = ("applab",)
    CONFIG_DIR = Path.home().joinpath(".applab")
    ACCOUNTS_FILE = CONFIG_DIR.joinpath("accounts.json")
````

## File: src/applab/README.md
````markdown
# applab root package

root package为`applab`namespace, `/src`不能放代码，uv 需要此空目录避免报错
````

## File: docs/README.md
````markdown
# 设计文档

## 架构

```txt
App（GUI界面：针对非技术用户）
 └── Preset / Recipe (安装约束 + 可选参数：针对技术用户）
      └── Infra Plan（具体要建什么：applab云封装）
           └── Cloud SDK
```


## 组件
````

## File: pkgs/applab-vendor-tencentcloud/src/applab/vendor/tencentcloud/__init__.py
````python
"""
Tencent Cloud Provider

[tencentcloud-sdk-python](https://github.com/TencentCloud/tencentcloud-sdk-python)
"""

from .tendentcloud import TencentCloudVendor
from .aliyun import AliyunVendor

__all__ = [
    "TencentCloudVendor",
    "AliyunVendor",
]
````

## File: pkgs/applab-vendor-tencentcloud/pyproject.toml
````toml
[project]
name = "applab-vendor-tencentcloud"
version = "0.0.2dev20251230153900"
license = { text = "MIT" }

description = "Add your description here"
readme = "README.md"
authors = [{ name = "Chen Peng" }]
urls = { "homepage" = "https://github.com/chen56/applab" }

requires-python = ">=3.12"
dependencies = [
    "applab-core",
    "nanoid>=2.0.0",
    "tencentcloud-sdk-python-cam>=3.1.20",
    "tencentcloud-sdk-python-common>=3.1.23",
    "tencentcloud-sdk-python-cvm>=3.1.14",
    "tencentcloud-sdk-python-tag>=3.0.1481",
]

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
# uv_build默认就使用 src/ 布局，不需要额外配置
build-backend = "uv_build"

[dependency-groups]
dev = [
    "keyring>=25.7.0",
    "pytest>=9.0.1",
]

#################################################################################
# uv PEP 420 namespace 子项目配置
#################################################################################

[tool.uv.build-backend]
# 开启命名空间支持 PEP 420
# https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages
# namespace = true 会导致uv关掉安全检查，没搞懂啥意思，反正够乱的
namespace = false
# PEP 420命名空间的module名需改为'.'分割，避免默认的'applab-core'
module-name = "applab.vendor.tencentcloud"

[tool.ruff]
cache-dir = "build/.ruff_cache"

[tool.pytest.ini_options]
cache_dir = "build/.pytest_cache"

[tool.uv.sources]
applab-core = { workspace = true }
````

## File: .gitignore
````
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py.cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# UV
#   Similar to Pipfile.lock, it is generally recommended to include uv.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#uv.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock
#poetry.toml

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#   pdm recommends including project-wide configuration in pdm.toml, but excluding .pdm-python.
#   https://pdm-project.org/en/latest/usage/project/#working-with-version-control
#pdm.lock
#pdm.toml
.pdm-python
.pdm-build/

# pixi
#   Similar to Pipfile.lock, it is generally recommended to include pixi.lock in version control.
#pixi.lock
#   Pixi creates a virtual environment in the .pixi directory, just like venv module creates one
#   in the .venv directory. It is recommended not to include this directory in version control.
.pixi

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
.idea/
!/.idea/dictionaries/

# Abstra
# Abstra is an AI-powered process automation framework.
# Ignore directories containing user credentials, local state, and settings.
# Learn more at https://abstra.io/docs
.abstra/

# Visual Studio Code
#  Visual Studio Code specific template is maintained in a separate VisualStudioCode.gitignore
#  that can be found at https://github.com/github/gitignore/blob/main/Global/VisualStudioCode.gitignore
#  and can be added to the global gitignore or merged into this file. However, if you prefer,
#  you could uncomment the following to ignore the entire vscode folder
# .vscode/

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

# Cursor
#  Cursor is an AI-powered code editor. `.cursorignore` specifies files/directories to
#  exclude from AI features like autocomplete and code analysis. Recommended for sensitive data
#  refer to https://docs.cursor.com/context/ignore-files
.cursorignore
.cursorindexingignore

# Marimo
marimo/_static/
marimo/_lsp/
__marimo__/


# macOS system files
.DS_Store


# quarto
.quarto/
**/*.quarto_ipynb

/.quarto/
````

## File: pkgs/applab-cli/src/applab/cli/_console.py
````python
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

from typing import Any, cast

from rich.console import Console
from typing import Dict, Literal

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
        self._print("🟢 ", *objects, style="primary")

    def warn(self, *objects: Any) -> None:
        self._print(":warning-emoji:", *objects, style="tertiary")

    def info(self, *objects: Any) -> None:
        self._print("ℹ️ ", *objects, style="surface_variant")

    def input(self, *objects: Any) -> None:
        self._print("🧷 ", *objects, style="surface")

    def error(self, *objects: Any) -> None:
        self._print("🔴 ", *objects, style="error")

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
````

## File: pkgs/applab-core/src/applab/core/_account.py
````python
import datetime
from abc import ABC, abstractmethod
from typing import Type, Annotated, List

from pydantic import BaseModel, Field, ConfigDict

from ._constant import APPLAB
from ._param_model import BaseParamModel
from .storage import JsonStorage

_ACCOUNT_ID_ALPHABET_ = "0123456789abcdefghijklmnopqrstuvwxyz"
_ACCOUNT_ID_LENGTH_ = 12


def _new_account_id_() -> str:
    from nanoid import generate

    return generate(_ACCOUNT_ID_ALPHABET_, _ACCOUNT_ID_LENGTH_)


def _keyring_key_(account_id: str) -> str:
    return f"{APPLAB.APP_NAME}.account.{account_id}"


class CredentialParam(BaseParamModel):
    title: Annotated[str, Field(title="Credential Title")] = "default"


class Account(BaseModel):
    id: Annotated[str, Field(init=False, default_factory=_new_account_id_)]
    vendor: str
    title: str
    is_default: bool = False
    created_at: Annotated[
        datetime.datetime, Field(init=False, default_factory=lambda: datetime.datetime.now(datetime.UTC))
    ]

    model_config = ConfigDict(extra="allow")

    @property
    def credential_key(self) -> str:
        return _keyring_key_(self.id)


class Authenticator(ABC):
    @property
    @abstractmethod
    def credential_type(self) -> Type[CredentialParam]:
        pass

    @abstractmethod
    def authenticate(self, credential_param: CredentialParam) -> Account:
        pass


class AccountList[T:Account](BaseModel):
    accounts: List[T] = []


class AccountManager[T:Account]:
    def __init__(self, storage: JsonStorage[AccountList[T]]):
        self.storage = storage
        self.accounts: AccountList[T] = self.storage.load()

    def add(self, account: T):
        self.accounts.accounts.append(account)
        self.save()

    def set_default(self, account: T):
        for acc in self.accounts.accounts:
            acc.is_default = False
        account.is_default = True
        self.save()

    def save(self):
        self.storage.save(self.accounts)
````

## File: pkgs/applab-vendor-tencentcloud/src/applab/vendor/tencentcloud/aliyun.py
````python
from typing import Annotated, Type

from pydantic import SecretStr, Field

from applab.core import CredentialParam
from applab.core import Vendor
from applab.core import Authenticator


# ============================================================
# 模拟 applab_apps 包（vendor 实现）
# ============================================================


class AliyunAKSKCredentialParam(CredentialParam):
    access_key_id: Annotated[str, Field(title="AccessKey ID", description="Aliyun Cloud API AccessKey ID")]
    access_key_secret: Annotated[
        SecretStr, Field(title="AccessKey Secret", description="Aliyun Cloud API AccessKey Secret")
    ]


class AliyunAKSKAuthenticator(Authenticator):
    @property
    def credential_type(self) -> Type[AliyunAKSKCredentialParam]:
        return AliyunAKSKCredentialParam

    def authenticate(self, credential: AliyunAKSKCredentialParam):
        pass


class AliyunVendor(Vendor):
    def __init__(self, version: str):
        super().__init__(
            name="aliyun",
            display_name="阿里云",
            version=version,
            authenticator=AliyunAKSKAuthenticator(),
        )
````

## File: pkgs/applab-cli/pyproject.toml
````toml
[project]
name = "applab-cli"
version = "0.0.2dev20251230153900"
# dynamic = ["version"] # todo 后面用 dynamic 替换掉 version 字段
license = { text = "MIT" }

description = "Add your description here"
readme = "README.md"
authors = [{ name = "Chen Peng" }]
urls = { "homepage" = "https://github.com/chen56/applab" }

requires-python = ">=3.12"
dependencies = [
    "applab-core",
    "applab-vendor-tencentcloud",
    "cyclopts>=4.4.0",
    "pydantic>=2.12.5",
    "requests>=2.32.5",
    "rich>=14.2.0",
]

[dependency-groups]
dev = [
    "deepdiff>=8.6.1",
    "keyring>=25.7.0",
    "pytest>=9.0.1",
]



[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
# uv_build默认就使用 src/ 布局，不需要额外配置
build-backend = "uv_build"

[tool.uv.build-backend]
# 开启命名空间支持 PEP 420
# https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages
# namespace = true 会导致uv关掉安全检查，没搞懂啥意思，反正够乱的
namespace = false
# PEP 420命名空间的module名需改为'.'分割，避免默认的'applab-core'
module-name = "applab.cli"

[tool.ruff]
cache-dir = "build/.ruff_cache"

[tool.pytest.ini_options]
cache_dir = "build/.pytest_cache"
````

## File: pkgs/applab-core/pyproject.toml
````toml
[project]
name = "applab-core"
version = "0.0.2dev20251230153900"
# dynamic = ["version"] # todo 后面用 dynamic 替换掉 version 字段
license = { text = "MIT" }

description = "Add your description here"
readme = "README.md"
authors = [{ name = "Chen Peng" }]
urls = { "homepage" = "https://github.com/chen56/applab" }

requires-python = ">=3.12"
dependencies = [
    "cyclopts>=4.4.0",
    "platformdirs>=4.5.1",
    "pydantic>=2.12.5",
    "requests>=2.32.5",
    "rich>=14.2.0",
]

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
# uv_build默认就使用 src/ 布局，不需要额外配置
build-backend = "uv_build"

[dependency-groups]
dev = [
    "keyring>=25.7.0",
    "pytest>=9.0.1",
]

#################################################################################
# uv PEP 420 namespace 子项目配置
#################################################################################

[tool.uv.build-backend]
# 开启命名空间支持 PEP 420
# https://docs.astral.sh/uv/concepts/build-backend/#namespace-packages
# namespace = true 会导致uv关掉安全检查，没搞懂啥意思，反正够乱的
namespace = false
# PEP 420命名空间的module名需改为'.'分割，避免默认的'applab-core'
module-name = "applab.core"

[tool.ruff]
cache-dir = "build/.ruff_cache"

[tool.pytest.ini_options]
cache_dir = "build/.pytest_cache"
````

## File: pkgs/applab-vendor-tencentcloud/src/applab/vendor/tencentcloud/tendentcloud.py
````python
from typing import Annotated, Type

from pydantic import Field
from pydantic.types import SecretStr

from applab.core import Authenticator, CredentialParam, Account, Vendor, AccountManager
from applab.core import AccountList
from applab.core import APPLAB
from applab.core.storage import JsonStorage


class TencentCloudVendor(Vendor):
    def __init__(self, version: str):
        super().__init__(
            name="tencentcloud",
            display_name="腾讯云",
            version=version,
            authenticator=TencentCloudAKSKAuthenticator(),
            account_manager=AccountManager(
                storage=JsonStorage(path=APPLAB.CONFIG_DIR / "tencentcloud.json", model=AccountList[TencentCloudAccount]),
            ),
        )


class TencentCloudAKSKCredentialParam(CredentialParam):
    secret_id: Annotated[str, Field(title="SecretId", description="Tencent Cloud API SecretId")]
    secret_key: Annotated[SecretStr, Field(title="SecretKey", description="Tencent Cloud API SecretKey")]


class TencentCloudAccount(Account):
    vendor: str = "tencentcloud"
    app_id: int
    uin: str
    owner_uin: str


class TencentCloudAKSKAuthenticator(Authenticator):
    @property
    def credential_type(self) -> Type[TencentCloudAKSKCredentialParam]:
        return TencentCloudAKSKCredentialParam

    def authenticate(self, credential_param: TencentCloudAKSKCredentialParam):
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.cam.v20190116 import cam_client as cam, models as cam_models
        try:
            cred = credential.Credential(credential_param.secret_id, credential_param.secret_key.get_secret_value())

            client = cam.CamClient(cred, "ap-guangzhou")
            req = cam_models.GetUserAppIdRequest()
            resp = client.GetUserAppId(req)
            result = TencentCloudAccount(
                title=credential_param.title,
                app_id=resp.AppId,
                uin=resp.Uin,
                owner_uin=resp.OwnerUin,
            )

            return result
        except TencentCloudSDKException as err:
            print(f"登录失败: {err}")
            raise err
````

## File: sha.bash
````bash
#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略 xxx 函数未被使用的警告

set -o errtrace  # -E trap inherited in sub script
set -o errexit   # -e
set -o functrace # -T If set, any trap on DEBUG and RETURN are inherited by shell functions
set -o pipefail  # default pipeline status==last command status, If set, status=any command fail

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

cd "$(dirname "${BASH_SOURCE[0]}")"
source "./sha_common.bash"

##########################################
# app cmd script
# 独立于项目组的特殊命令
##########################################

##################################################
# 项目扩展命令集
##################################################

build() {
  echo "current:$(pwd)"
  check
  format
  _run uv build
}

publish() {
  # echo "$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)"
  local api_key
  api_key=$(uv run -m keyring get pypi_applab_api_token pypi_applab_api_token)
  _run uv publish -t "${api_key}"
}

sync() (
  # 同步ai所需文件
  # ln -sf ../.ai/CONTEXT.md .gemini/CONTEXT.md

  _run uv sync --all-extras --all-groups
  _run repomix
  _run quarto render .ai/context.qmd

)


format() {
  # _run uv run ruff check --fix
  # _run uv run ruff format
  echo todo format
}

test() {
  _run uv run pytest tests/
}

check() {
  echo todo check
  # _run uv run pyright --pythonplatform Darwin
  # _run uv run pyright --pythonplatform Linux
  # _run uv run pyright --pythonplatform Windows
  _run uv run ruff check --fix
}


info() {
  echo "sha run at: $(pwd)"
}

# gemini() {
#   # export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) 
#   env GOOGLE_CLOUD_PROJECT="$(gcloud config get-value project)" command  gemini "$@"
# }

##########################################
# app 入口
##########################################
# 守卫语句，本脚本如果作为lib导入使用则不再执行后续命令入口代码
# - 当本脚本作为命令被执行时'$ ./sha', $0为'./sha,
# - 当本脚本当作类库导入时即: '. ./sha'，$0值为bash/zsh等
# 类似python的'if __name__ == "__main__"'
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  # 命令式执行的入口代码, 即'$ ./sha' 而不是'. ./sha'
  sha "$@"
fi
````

## File: pkgs/applab-cli/src/applab/cli/__init__.py
````python
"""applab.cli.

没有export的模块，只提供cli的入口函数。
"""

from .main import main

__all__ = ["main"]
````

## File: pkgs/applab-cli/src/applab/cli/_cmd_account.py
````python
import inspect

from cyclopts import App, Parameter
from applab.core import Vendor, Authenticator, Applab
from ._console import console


class AccountApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="account",
            help="""
            Cloud account management.
            """,
        )
        self.app.command(self.list_, name="list")
        self.app.command(self.info)
        self.app.command(AccountLoginApp(applab).app, name="login")

    def list_(self):
        """
        列出所有已保存的云账户信息。
        """
        from rich.table import Table
        table = Table(title="Cloud Accounts", show_lines=True)
        table.add_column("Vendor")
        table.add_column("Account Name")
        table.add_column("Account ID")
        table.add_column("Default")
        table.add_column("Created At")
        for vendor in self.applab.vendors.values():
            for acc in vendor.account_manager.accounts.accounts:
                table.add_row(acc.vendor, acc.title, acc.id, str(acc.is_default), str(acc.created_at))
        console.print(table)

    def info(self, vendor_name: str):
        """
        展示指定云厂商的账户详情（优先展示默认账户）。
        """
        vendor = self.applab.vendors.get(vendor_name)
        if not vendor or not vendor.account_manager or not vendor.account_manager.accounts.accounts:
            console.error(f"未找到厂商 {vendor_name} 的账户信息。")
            return 1

        accounts = vendor.account_manager.accounts.accounts
        default_acc = next((a for a in accounts if a.is_default), accounts[0])
        console.print(default_acc)
        return 0


class AccountLoginApp:
    def __init__(self, applab: Applab):
        self.applab = applab
        self.app = App(
            name="login",
            help="""
                Cloud account login.
                """,
        )

        def _create_login_handler(vendor: Vendor, authenticator: Authenticator):
            @Parameter(name="*")
            class DynamicParam(authenticator.credential_type):
                pass

            def login_handler(*, param: DynamicParam):

                console.info(f"正在登录 {vendor.name}...{param=}")
                account = authenticator.authenticate(param)
                console.success(f"已成功登录 {vendor.name}")
                vendor.account_manager.add(account)
                console.info(f"已保存账号到 {vendor.account_manager.storage.path}")
                return 0

            return login_handler

        for vendor in applab.vendors.values():
            authenticator_doc = inspect.cleandoc(vendor.authenticator.__doc__ or "")
            cmd_help = f"""
                {vendor.display_name}({vendor.name}) login.

                **认证逻辑:**

                {authenticator_doc}
            """
            self.app.command(name=vendor.name, help=inspect.cleandoc(cmd_help or ""))(
                _create_login_handler(vendor, vendor.authenticator))
````

## File: shab.bash
````bash
#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略 xxx 函数未被使用的警告

set -o errtrace  # -E trap inherited in sub script
set -o errexit   # -e
set -o functrace # -T If set, any trap on DEBUG and RETURN are inherited by shell functions
set -o pipefail  # default pipeline status==last command status, If set, status=any command fail

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT_DIR" # 保证后续命令都在当前项目下执行

source "./sha_common.bash"

##########################################
# app cmd script
# 独立于项目组的特殊命令
##########################################

info() {
  echo "## workspaces:"
  xxx() {
    echo i am xxx
  }
}

build() {
  check
  format
  _run uv build --all-packages
}

publish() {
  # echo "$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)"
  local api_key
  api_key=$(uv run -m keyring get pypi_applab_api_token pypi_applab_api_token)
  uv publish -t "${api_key}"
}

sync() (
  _run uv sync --all-extras --all-groups --all-packages
  _run ./sha.bash sync
)


check() {
  _run uv run ruff check --fix
  echo todo ruff
}

lintfix() {
  _run uv run ruff check --fix
}

format() {
  _run uv run ruff format
}

test() {
  _run uv run pytest
}

sync_github() {
  # --- 尽量与 Conventional Commits 对应 ---
  _run gh label create "type:pm"                           -f  --color "ff9800" --description "项目管理" # 橙色
  _run gh label create "type:devflow"                      -f  --color "ff9800" --description "优化开发流,比如集成ai native开发方法, 用Changesets更好控制版本发布等" # 橙色
  _run gh label create "type:question"                     -f --color "ff9800" --description "待解答问题" # 橙色
  _run gh label create "type:help wanted"                  -f --color "9e9e9e" --description "需要帮助" # 灰色
  _run gh label create "type:bug"                          -f  --color "f44336" --description "Bug 报告" # 红色
  _run gh label create "type:feat"                         -f  --color "4caf50" --description "功能请求" # 绿色
  _run gh label create "type:enhancement"                  -f --color "ff9800" --description "现有功能的改进或增强" # 橙色
  _run gh label create "type:docs"                         -f --color "2196f3" --description "文档、提示语更新" # 蓝色
  _run gh label create "type:test"                         -f --color "9e9e9e" --description "测试相关的 Issue（例如，缺少测试）" # 灰色
  _run gh label create "type:perf"                         -f --color "e91e63" --description "性能优化问题" # 粉红色
  _run gh label create "type:chore"                        -f --color "607d8b" --description "杂项任务或不会影响功能的改动（例如配置文件更新）" # 深灰色
  _run gh label create "type:build"                        -f --color "9e9e9e" --description "构建过程或构建系统问题" # 灰色
  _run gh label create "type:ci"                           -f --color "9e9e9e" --description "持续集成（CI）问题" # 灰色
  _run gh label create "type:refactor"                     -f  --color "ffc107" --description "代码重构" # 黄色
  _run gh label create "type:style"                        -f --color "673ab7" --description "代码风格或格式相关的更新，通常不影响功能" # 紫色
  _run gh label create "type:revert"                       -f --color "673ab7" --description "撤销（revert）某个功能或改动" # 紫色
  _run gh label create "priority:P0".                      -f --color "b71c1c" --description "紧急，需立即处理" # 深红色
  _run gh label create "priority:P1".                      -f --color "ff5722" --description "高优先级" # 橙色
  _run gh label create "priority:P2".                      -f --color "388e3c" --description "低优先级" # 绿色
  _run gh label create "module:applab"                     -f --color "0d47a1" --description "root 模块 applab" # 深蓝
  _run gh label create "module:applab-core"                -f --color "1976d2" --description "applab-core 模块" # 蓝色
  _run gh label create "module:applab-vendor-tencentcloud" -f --color "0277bd" --description "applab-vendor-tencentcloud" # 更深的蓝色
  _run gh label create "module:applab-vendor-aliyun"       -f --color "0288d1" --description "applab-vendor-aliyun" # 蓝色
  _run gh label create "scope:api"                         -f --color "0d47a1" --description "API 相关问题" # 深蓝
  _run gh label create "scope:frontend"                    -f --color "1976d2" --description "前端相关问题" # 蓝色
  _run gh label create "scope:backend"                     -f --color "0288d1" --description "后端相关问题" # 蓝色
  _run gh label create "scope:security"                    -f --color "0288d1" --description "安全相关问题" # 蓝色
  _run gh label create "state:duplicate"                   -f --color "f44336" --description "重复问题" # 红色
  _run gh label create "state:wontfix"                     -f --color "607d8b" --description "不会修复" # 深灰色
  _run gh label create "state:invalid"                     -f --color "9e9e9e" --description "无效问题" # 灰色
}                  

##########################################
# app 入口
##########################################
# 守卫语句，本脚本如果作为lib导入使用则不再执行后续命令入口代码
# - 当本脚本作为命令被执行时'$ ./sha', $0为'./sha,
# - 当本脚本当作类库导入时即: '. ./sha'，$0值为bash/zsh等
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  # 命令式执行的入口代码, 即'$ ./sha' 而不是'. ./sha'
  sha "$@"
fi
````

## File: pkgs/applab-cli/src/applab/cli/main.py
````python
"""cli main入口"""
import logging
import os

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
        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(name)s: "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        # https://rich.readthedocs.io/en/stable/logging.html
        handlers=[RichHandler(rich_tracebacks=True)],
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
    # applab.vendors.register(tencentcloud.AliyunVendor(version=version))

    ApplabCli(applab).app()


if __name__ == "__main__":
    main()
````

## File: pkgs/applab-core/src/applab/core/__init__.py
````python
"""applab.core

提供核心业务逻辑相关的工具。
"""

from ._param_model import BaseParamModel, TextField, UIField
from ._base import Vendor, VendorRegister, Applab
from ._account import CredentialParam, Authenticator, Account, AccountManager, AccountList
from .storage import JsonStorage
from ._constant import APPLAB
__all__ = [
    # _arg_model
    "BaseParamModel",
    "TextField",
    "UIField",
    # _auth
    "CredentialParam",
    "Authenticator",
    "Account",
    "AccountManager",
    "AccountList",
    # _base
    "Applab",
    "Vendor",
    "VendorRegister",
    # _constant
    "APPLAB",
    # _storage
    "JsonStorage",
]
````

## File: pkgs/applab-core/src/applab/core/_base.py
````python
import json
from abc import ABC
from collections.abc import Mapping

from ._account import Authenticator, AccountManager


class Vendor(ABC):
    def __init__(
            self,
            name: str,
            display_name: str,
            authenticator: Authenticator,
            account_manager: AccountManager,
            version: str = "0.0.1",
    ):
        # 实例属性（可变字段）
        self.name = name
        self.display_name = display_name
        self.version = version
        self.authenticator = authenticator
        self.account_manager = account_manager

    def info(self) -> dict:
        """返回 vendor 信息字典."""
        return {
            "name": self.name,
            "version": self.version,
        }

    def __str__(self):
        return json.dumps(self.info())


class VendorRegister(Mapping[str, Vendor]):
    """只读 Provider 注册表."""

    def __init__(self):
        self._delegate: dict[str, Vendor] = {}

    def register(self, vendor: Vendor):
        """注册 Provider 类."""
        self._delegate[vendor.name] = vendor

    # Mapping 接口
    def __getitem__(self, key) -> Vendor:
        return self._delegate[key]

    def __iter__(self):
        return iter(self._delegate)

    def __len__(self):
        return len(self._delegate)


class Applab:
    def __init__(
            self,
            vendors: VendorRegister = VendorRegister(),
    ):
        self.vendors = vendors
````

## File: pyproject.toml
````toml
[project]
name = "applab"
version = "0.0.2dev20251230153900"
# dynamic = ["version"] # todo 后面用 dynamic 替换掉 version 字段
license = { text = "MIT" }

description = "Aggregator package for all applab subpackages"
readme = "README.md"
authors = [{ name = "Chen Peng" }]
urls = { "homepage" = "https://github.com/chen56/applab" }

requires-python = ">=3.12"
# Aggregator package for all applab subpackages
# 统一依赖所有子包
dependencies = [
    "applab-core",
    "applab-cli",
    "applab-vendor-tencentcloud",
]

[dependency-groups]
# quarto deps: jupyter
dev = [
    "pytest>=9.0.1",
    "ruff>=0.14.10",
    "ty>=0.0.8",
    "pyrefly>=0.46.3",
    "keyring>=25.7.0",
    "jupyter>=1.1.1",
]

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
# uv_build默认就使用 src/ 布局，不需要额外配置
build-backend = "uv_build"

[project.scripts]
applab = "applab.cli:main"

#################################################################################
# uv
#################################################################################

[tool.uv.build-backend]
namespace = true
module-name = ["applab"]
module-root = "src"


[tool.uv.workspace]
# `uv workspace metadata` 看效果
members = [
    "pkgs/*",
]


[tool.uv.sources]
applab-cli = { workspace = true }
applab-core = { workspace = true }
applab-vendor-tencentcloud = { workspace = true }

[tool.uv]
# workspace 根虽然没代码，但作为聚合包
package = true

# `uv python install`的不是官网文件，而是这个项目打包的便携版: https://github.com/astral-sh/python-build-standalone/
# 镜像较少，参考: https://github.com/tuna/issues/issues/2125
# 已知镜像站点：
# - https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone/
# - https://registry.npmmirror.com/-/binary/python-build-standalone/
# - https://gh-proxy.com/github.com/indygreg/python-build-standalone/releases/download
# 镜像下载示例：
# - uv python install --mirror https://registry.npmmirror.com/-/binary/python-build-standalone/ 3.12
# - UV_PYTHON_INSTALL_MIRROR=https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone/ uv python install 3.12
# pyproject.toml config ref: https://docs.astral.sh/uv/reference/settings/#python-install-mirror
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone/"

[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple/"
[[tool.uv.index]]
url = "https://mirrors.aliyun.com/pypi/simple/"

#################################################################################
# --- Ruff 配置（更新为 NumPy 风格） ---
#################################################################################

[tool.ruff]
cache-dir = "build/.ruff_cache"
src = ["."]
exclude = [".git", "__pycache__", "build", "dist", ".venv"]
line-length = 120

[tool.ruff.lint]
ignore = [
    "D100", # Missing docstring in a public module
    "D101", # Missing docstring in a public class
    "D102", # Missing docstring in a public method
    "D103", # Missing docstring in a public function
    "D104", # Missing docstring in a public package
    "D105", # undocumented-magic-method (D105)
    "D107", # Missing docstring in a public nested class
    "D205", # 1 blank line required after the summary line
    "D400",# missing-trailing-period
    "D401", # The first line should be imperative
    "E501", # Line too long
    "W293", # Blank line contains whitespace
]

select = [
    "E", # pycodestyle Errors
    "W", # pycodestyle Warnings
    "F", # Pyflakes
    "B", # Bugbear
]
extend-select = [
    "UP", # pyupgrade
    "D", # pydocstyle
]

[tool.ruff.lint.per-file-ignores]
"**/{tests,docs,tools}/**" = [
    "D102", # Missing docstring in a public method
    "D106", # Missing docstring in a public nested class
]

[tool.ruff.lint.pydocstyle]
convention = "numpy" # 使用 NumPy 风格的 docstring 约定

#################################################################################
# pytest
#################################################################################

[tool.pytest.ini_options]
cache_dir = "build/.pytest_cache"

#################################################################################
# pyright
#################################################################################
# [tool.pyright]
# include = [
#     # "src", # 根项目暂时无代码
#     # "tests",
#     "pkgs/*/src", #Mono 子项目
#     "pkgs/*/tests",
# ]
# exclude = ["**/node_modules", "**/__pycache__"]
# ignore = ["src/oldstuff"]
# defineConstant = { DEBUG = true }
# # stubPath = "src/stubs"

# reportMissingImports = "error"
# reportMissingTypeStubs = false

# pythonVersion = "3.12" # 根环境默认用最新版本，兼容多平台特性

# 根环境默认平台（可任选，子环境覆盖），不配置按照当前运行平台
# 目前pyright无法配置检查多个平台，可用用uv run pyright --pythonplatform Darwin 参数多次检查
# pythonPlatform = "Darwin"

# 可用executionEnvironments 对特定目录指定特定平台




#################################################################################
# ty ty的vscode插件不行，会扰乱vscode
#################################################################################


[tool.ty.environment]
# Tailor type stubs and conditionalized type definitions to windows.
python-platform = "all"
python-version = "3.12"
# Multiple directories (priority order)
#root = ["./src", "./tests"]

[[tool.ty.overrides]]
#include = ["src"]
exclude = [".venv"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "error"

#################################################################################
# pyrefly
#################################################################################

# Pyrefly header
[tool.pyrefly]

#### configuring what to type check and where to import from

project-includes = ["**/*.py*"]

#project-excludes = ["**/node_modules", "**/__pycache__", "**/*venv/**", "**/.[!/.]*/**"]
source_roots = ["."]

search-path = ["."]
site-package-path = ["venv/lib/python3.12/site-packages"]

#### configuring your python environment
# python-platform = "linux"
python-version = "3.12"
# python-interpreter-path = "venv/bin/python3"

#### configuring your type check settings
replace-imports-with-any = [
    #   "sympy.*",
    #   "*.series",
]

ignore-errors-in-generated-code = true

[tool.pyrefly.errors]
# bad-assignment = false
# invalid-argument = false
````
