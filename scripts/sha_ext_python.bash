#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略 xxx 函数未被使用的警告

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

##################################################
# 项目扩展命令集
##################################################

build() {
  clean
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
  _run uv sync --all-extras --all-groups
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
  # _run uv run ruff check
}