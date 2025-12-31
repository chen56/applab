#!/usr/bin/env bash

MODULE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "$MODULE_DIR/../.." && pwd)
source "$ROOT_DIR/sha.bash"
cd "$MODULE_DIR"

##########################################
# app cmd script
# 独立于项目组的特殊命令
##########################################

##########################################
# app 入口
##########################################
# 守卫语句，本脚本如果作为lib导入使用则不再执行后续命令入口代码
# - 当本脚本作为命令被执行时'$ ./sha', $0为'./sha,
# - 当本脚本当作类库导入时即: '. ./sha'，$0值为bash/zsh等
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  sha "$@"
fi