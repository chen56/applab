#!/usr/bin/env bash

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

# On Mac OS, readlink -f doesn't work, so use._real_path get the real path of the file
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

_install_sha() (
  mkdir -p "$ROOT_DIR/vendor"
  set -x
  curl -L -o "$ROOT_DIR/vendor/sha.bash" https://github.com/chen56/sha/raw/main/sha.bash
)

if ! [[ -f "$ROOT_DIR/vendor/sha.bash" ]]; then
  _install_sha
fi

# 注意!!! `source "$ROOT_DIR/vendor/sha.bash"` 执行后定义的函数才被注册为sha命令
# shellcheck disable=SC1091 # 忽略：Not following: ./vendor/sha.bash was not specified as input
source "$ROOT_DIR/vendor/sha.bash"

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
  caller_script=$(caller 0 | awk '{print $3}')
  caller_line=$(caller 0 | awk '{print $1}')
  # 把 /home/ubuntu/current_work_dir 替换为 ~/current_work_dir 短格式
  # 使用 @ 作为分隔符，避免与路径中的 / 冲突
  # shellcheck disable=SC2001
  show_pwd=$(echo "$PWD" | sed "s@^$HOME@~@" )

  echo "  🔵$caller_script:$caller_line ${FUNCNAME[1]}() ▶︎【$show_pwd$ $*】" >&2
  "$@"
}




##################################################
# 每个项目的公共命令集
##################################################

sync() (
  uv sync
  uv pip install -e . # 确保src目录被安装为可编辑模式，让import正常工作，避免使用PYTHONPATH
)

resync() (
  clean
  _run rm -rf .venv
  sync
)

clean() (
  _run rm -rf build dist ./*.egg-info
  _run rm -rf .pytest_cache .mypy_cache .coverage
)

test() {
  uv run pytest tests/
}

# shellcheck disable=SC2329 # 忽略This function is never invoked
tools() {
  info() {
    echo "本项目使用的命令框架：https://github.com/chen56/sha"
  }
  update() {
    _install_sha
  }
}