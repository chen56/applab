#!/usr/bin/env bash

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

# On Mac OS, readlink -f doesn't work, so use._real_path get the real path of the file
TOOLS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# shellcheck disable=SC1091
source "$TOOLS_DIR/sha_common.bash"

##################################################
# 可以为每个项目添加的公共命令集
##################################################

clean() (
  _run rm -rf build dist
)

# shellcheck disable=SC2329 # 忽略This function is never invoked
tools() {
  info() {
    echo "本项目使用的命令框架：https://github.com/chen56/sha"
  }
  update() {
    _install_sha
  }
}