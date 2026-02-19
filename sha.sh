#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略函数未被使用的警告

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
  _run rm -rf .gemini/skills && ln -fs ../.agent/skills .gemini/skills
  _run rm -rf .qwen/skills   && ln -fs ../.agent/skills .qwen/skills
  _run rm -rf .trae/skills   && ln -fs ../.agent/skills .trae/skills

  _run uv sync --all-extras --all-groups
  _run rsync -av --delete .agent build/
  # _run repomix
  # _run quarto render ai/context.qmd

)

dev() {
    
  up() {
    if [[ ! -f .env ]]; then
      _run cp .env.template .env
      _print warning "Created .env from .env.template. Please edit it with your secrets."
    fi

    if command -v devcontainer >/dev/null 2>&1; then
      _print info "Using devcontainer CLI..."
      _run devcontainer up --workspace-folder .
    else
      _print warning "devcontainer CLI not found, falling back to docker compose..."
      _run docker compose -f .devcontainer/docker-compose.yml up -d --build
      _print info "Remember to run 'uv sync' inside the container."
    fi
  }
  # down
  down() {
    _run docker compose -f .devcontainer/docker-compose.yml down
  }

}

# 太慢了，还有输入选项，单独安装吧
sync_skills() {
  # 查找所有不要的目录，skills add 若不指定--agent则增加一堆目录
  # find ~ -maxdepth 1 -type d -name '.*' -not -path '*/.Trash' -not -path './.Trash/*' -not -path './.gemini/*' -not -path './.qwen/*' -not -path './.agent/*' -not -path './.agents/*' -exec find {}  -type d -name 'skills' -maxdepth 1 \; | xargs -I {} dirname '{}'
  _run npx skills add --agent gemini-cli -y https://github.com/anthropics/skills --skill skill-creator
  _run npx skills add --agent gemini-cli -y https://github.com/vercel-labs/skills --skill find-skills
  _run npx skills add --agent gemini-cli -y https://github.com/othmanadi/planning-with-files --skill planning-with-files

  _run rm -rf .gemini/skills && ln -fs ../.agent/skills .gemini/skills
  _run rm -rf .qwen/skills   && ln -fs ../.agent/skills .qwen/skills

}

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

gemini() {
  # export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) 
  env GOOGLE_CLOUD_PROJECT="$(gcloud config get-value project)" command  gemini "$@"
}

qwen() {
  command  qwen -s "$@"
}

update() {
  _run pnpm install -g @google/gemini-cli@latest
  _run pnpm install -g @qwen-code/qwen-code@latest

  _install_sha

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