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
  _run repomix
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