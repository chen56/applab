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

source "./scripts/sha_common.bash"
source "./scripts/sha_ext.bash"

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
  clean
  lint
  format
  uv build --all-packages "$@"
}

publish() {
  # echo "$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)"
  local api_key
  api_key=$(uv run -m keyring get pypi_org_paq_api_key pypi_org_paq_api_key)
  uv publish -t "${api_key}"
}

sync() (
  _run uv sync --all-extras --all-groups --all-packages
  # uv pip install -e . # 确保src目录被安装为可编辑模式，让import正常工作，避免使用PYTHONPATH
)


lint() {
  # uv run ruff check
  echo todo ruff
}

lintfix() {
  uv run ruff check --fix
}

format() {
  uv run ruff format
}

test() {
  uv run pytest
}


##########################################
# app 入口
##########################################
# 守卫语句，本脚本如果作为lib导入使用则不再执行后续命令入口代码
# - 当本脚本作为命令被执行时'$ ./sha', $0为'./sha,
# - 当本脚本当作类库导入时即: '. ./sha'，$0值为bash/zsh等
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  return 0
fi

# 命令式执行的入口代码, 即'$ ./sha' 而不是'. ./sha'
sha "$@"
