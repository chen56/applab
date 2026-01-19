# github规范

## github label 规范

[sha.bash](../shab.bash) 的sync_github函数定义了 github label，内容如下：

```bash
# --- 核心类型 (尽量与 Conventional Commits 对应) ---
  gh label create "type:pm"   -f  --color "ff9800" --description "项目管理" # 橙色
  gh label create "type:question" --color "ff9800" --description "待解答问题" # 橙色
  gh label create "type:help wanted" -f --color "9e9e9e" --description "需要帮助" # 灰色

  gh label create "type:bug"   -f  --color "f44336" --description "Bug 报告" # 红色
  gh label create "type:feat"  -f  --color "4caf50" --description "功能请求" # 绿色
  gh label create "type:enhancement" -f --color "ff9800" --description "现有功能的改进或增强" # 橙色
  gh label create "type:docs"     -f --color "2196f3" --description "文档、提示语更新" # 蓝色
  gh label create "type:test"     -f --color "9e9e9e" --description "测试相关的 Issue（例如，缺少测试）" # 灰色
  gh label create "type:perf"     -f --color "e91e63" --description "性能优化问题" # 粉红色
  gh label create "type:chore"    -f --color "607d8b" --description "杂项任务或不会影响功能的改动（例如配置文件更新）" # 深灰色
  gh label create "type:build"    -f --color "9e9e9e" --description "构建过程或构建系统问题" # 灰色
  gh label create "type:ci"       -f --color "9e9e9e" --description "持续集成（CI）问题" # 灰色
  gh label create "type:refactor" -f  --color "ffc107" --description "代码重构" # 黄色
  gh label create "type:style"    -f --color "673ab7" --description "代码风格或格式相关的更新，通常不影响功能" # 紫色
  gh label create "type:revert"   -f --color "673ab7" --description "撤销（revert）某个功能或改动" # 紫色

  # --- 优先级 (Priority) ---
  gh label create "priority:P0" -f --color "b71c1c" --description "紧急，需立即处理" # 深红色
  gh label create "priority:P1" -f --color "ff5722" --description "高优先级" # 橙色
  gh label create "priority:P2" -f --color "388e3c" --description "低优先级" # 绿色
  
    # --- 业务模块 (AppLab 专属) ---
  # --- 业务模块 (AppLab 专属) ---
  gh label create "module:applab"                     -f --color "0d47a1" --description "root 模块 applab" # 深蓝
  gh label create "module:applab-core"                -f --color "1976d2" --description "applab-core 模块" # 蓝色
  gh label create "module:applab-vendor-tencentcloud" -f --color "0277bd" --description "applab-vendor-tencentcloud" # 更深的蓝色
  gh label create "module:applab-vendor-aliyun"       -f --color "0288d1" --description "applab-vendor-aliyun" # 蓝色

  # --- 业务模块 (Scope) ---
  gh label create "scope:api"      -f --color "0d47a1" --description "API 相关问题" # 深蓝
  gh label create "scope:frontend" -f --color "1976d2" --description "前端相关问题" # 蓝色
  gh label create "scope:backend"  -f --color "0288d1" --description "后端相关问题" # 蓝色
  gh label create "scope:security" -f --color "0288d1" --description "安全相关问题" # 蓝色

  gh label create "state:duplicate" -f --color "f44336" --description "重复问题" # 红色
  gh label create "state:wontfix"   -f --color "607d8b" --description "不会修复" # 深灰色
  gh label create "state:invalid"   -f --color "9e9e9e" --description "无效问题" # 灰色
```
