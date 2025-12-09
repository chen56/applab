#!/usr/bin/env bash

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

##################################################
# 项目扩展命令集
##################################################

info() {
  echo "## workspaces:"
  # shellcheck disable=SC2154
  printf "  %s\n" "${__all_workspaces[@]}"
  echo "## packages:"
#  printf "  %s\n" "$(_dir_to_package_name "${__all_workspaces[@]}")"
#  echo "## out ip:"
#  echo "  $(curl ipinfo.io/ip 2>/dev/null)"
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

clean() (
  _run rm -rf .venv
  _run rm -rf .ruff_cache
  _run rm -rf build dist ./**/*.egg-info
  _run rm -rf .pytest_cache .mypy_cache .coverage
  _run find . \
        -path "./.venv" -prune -o \
        -path "./.git" -prune -o \
        -path "./dist" -prune -o \
        -name "__pycache__" -type d -exec rm -rf {} +
)