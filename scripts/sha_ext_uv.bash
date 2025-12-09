#!/usr/bin/env bash

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

##################################################
# 项目扩展命令集
##################################################

build() {
  clean
  lint
  format
  uv build "$@"
}

publish() {
  # echo "$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)"
  local api_key
  api_key=$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)
  uv publish -t "${api_key}"
}

sync() (
  clean
  uv sync
  # uv pip install -e . # 确保src目录被安装为可编辑模式，让import正常工作，避免使用PYTHONPATH
)

lint() {
  uv run ruff check
}

lintfix() {
  uv run ruff check --fix
}

format() {
  uv run ruff format
}

test() {
  uv run pytest tests/
}
