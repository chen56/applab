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


info() {
  echo "sha run at: $(pwd)"
}
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