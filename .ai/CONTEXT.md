# Applab 项目基准 Context 文件

## 项目概述

Applab 是云应用部署工具，旨在通过插件化设计支持多厂商集成（如腾讯云）.

## Architecture

* 项目采用**monorepo workspace** 结构，使用 uv 作为构建系统.
* 每个子包都有自己的 `pyproject.toml` 文件, 用于管理依赖和构建. 
* 遵循 PEP 420 命名空间包规范.

## 项目结构

```
applab/
├── pkgs/
│   ├── applab-cli/          # 命令行界面组件
│   ├── applab-core/         # 核心功能库
│   └── applab-vendor-tencentcloud/  # 腾讯云厂商适配器
├── src/
│   └── applab/              # 命名空间包根目录
├── README.md
└── pyproject.toml          # 根聚合包配置
```

## 核心技术栈

* **Language:** Python 3.12+
* **Package Manager:** `uv` (handles dependencies, virtual environments, and workspace resolution).
* **CLI Framework:** `cyclopts`.
* **Validation:** `pydantic`.
* **Testing:** `pytest`.
* **Linting/Formatting:** `ruff` (configured for NumPy style docstrings).
* **Type Checking:** `pyrefly` (experimental/configured).

## 子模块

### applab-core

核心功能库，提供通用类、异常、断言、参数模型等基础功能。

- **技术栈**: Python >=3.12, Pydantic v2, Cyclopts, Requests, Rich
- **功能**:
  - 账号认证管理
  - 参数校验模型
  - 断言和错误处理
  - 存储抽象
  - 常量定义

### applab-cli

命令行界面组件，提供用户交互入口。

- **技术栈**: 基于 core 组件，使用 Cyclopts 作为 CLI 框架
- **功能**:
  - 命令解析和执行
  - 账号管理命令
  - 控制台输出美化

### applab-vendor-tencentcloud

腾讯云厂商适配模块，用于对接腾讯云服务。

- **技术栈**: 基于 core 组件，使用腾讯云官方 SDK
- **功能**:
  - 腾讯云账号认证
  - 资源管理接口封装
  - 与 core 组件集成

## 开发规范

### 提交规范

项目遵循 [Conventional Commits v1.0.0](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 提交规范。

### 代码规范

- **Python 版本**: >=3.12
- **代码风格**: Ruff 检查，采用 NumPy 风格的 docstring
- **行长度**: 120 字符
- **文档规范**: 使用 NumPy 风格的文档字符串

### 构建系统

- **构建工具**: uv (版本 >=0.9.15)
- **包管理**: uv_build backend
- **命名空间**: PEP 420 命名空间包

## 配置文件

### 根 pyproject.toml

- 定义整个工作区的配置
- 聚合所有子包作为依赖项
- 配置了国内镜像源（清华源和阿里源）
- 定义了 Ruff、Pyrefly 等开发工具

### 子包配置

每个子包都有独立的 pyproject.toml，定义各自的依赖关系和构建配置。

## 认证机制

项目支持多种云服务提供商的认证方式：

| 云厂商 | ID 类凭据     | Secret 类凭据     | 关键参数                   |
| ------ | ------------- | ----------------- | -------------------------- |
| AWS    | access_key_id | secret_access_key | region_name                |
| 腾讯云 | secret_id     | secret_key        | -                          |
| 阿里云 | access_key_id | access_key_secret | -                          |
| Azure  | client_id     | client_secret     | tenant_id, subscription_id |
| GCP    | client_email  | private_key       | project_id                 |

## 开发环境设置

```bash
# 安装依赖
cd pkgs/applab-cli && uv sync
cd pkgs/applab-core && uv sync
cd pkgs/applab-vendor-tencentcloud && uv sync

# 运行测试
cd pkgs/applab-* && pytest

# 构建包
cd pkgs/* && uv build
```

## 工作流

1. 用户通过 CLI 调用命令
2. CLI 解析并调用 core 中的业务逻辑
3. Core 调用具体 vendor 实现或通用工具完成操作

## 设计模式

- **插件化架构**: 通过独立的 vendor 包实现对不同云厂商的支持
- **分层设计**:
  - CLI 层（applab-cli）
  - 核心逻辑层（applab-core）
  - 外部依赖/适配层（vendor packages）

## 测试策略

- 单元测试使用 pytest
- CLI 功能测试
- 账号管理测试
- 供应商集成测试


## github 规范

如需操作github相关事宜，请用`read_file`加载: [github规范](rules/github.md). 

