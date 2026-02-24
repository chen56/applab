# Applab

## Overview

Applab is a cloud application deployment tool designed with a plugin
architecture to support multiple cloud vendors (e.g., Tencent Cloud).

## Technical Architecture

- **Structure**: Monorepo workspace using `uv`.
- **Packaging**: PEP 420 Namespace Packages.
- **Stack**:
  - **Language**: Python 3.12+
  - **Manager**: `uv` (Dependency & Workspace)
  - **CLI**: `cyclopts`
  - **Validation**: `pydantic`
  - **Testing**: `pytest`
  - **Linting**: `ruff` (NumPy style docstrings)

## Project Structure

``` text
applab/
├── pkgs/
│   ├── applab-cli/          # CLI Entry & UX
│   ├── applab-core/         # Core Logic (Auth, Storage, Models)
│   └── applab-vendor-*/     # Vendor Adapters (e.g., tencentcloud)
├── src/
│   └── applab/              # Namespace Root
├── ai/                     # AI Context & Rules
└── pyproject.toml           # Workspace Config
```

## Modules

- **applab-core**: Universal classes, assertions, auth management,
  storage abstraction.
- **applab-cli**: CLI logic, command parsing (Cyclopts), console output.
- **applab-vendor-**\*: Cloud provider implementations (Auth, Resource
  Management).

## Development

### Environment

- **Setup**: `uv sync` (Syncs entire workspace)
- **Test**: `pytest` or `./sha test`
- **Build**: `uv build` or `./sha build`

### Standards

- **Commits**: [Conventional
  Commits](https://www.conventionalcommits.org/).
- **Code Style**: Ruff, NumPy docstrings, 120 line length.
- **Git Operations**: Do NOT perform `git add`, `commit`, `push` or
  other state-changing git commands unless explicitly instructed by the
  user.

## Authentication

| Vendor  | ID Credential | Secret Credential | Key Params                 |
|:--------|:--------------|:------------------|:---------------------------|
| AWS     | access_key_id | secret_access_key | region_name                |
| Tencent | secret_id     | secret_key        | \-                         |
| Aliyun  | access_key_id | access_key_secret | \-                         |
| Azure   | client_id     | client_secret     | tenant_id, subscription_id |
| GCP     | client_email  | private_key       | project_id                 |

## References

- **GitHub Rules**: [See Rules](build/ai/rules/github.md) (Load via `read_file`
  if needed).

## 禁止的/危险的操作 (Forbidden/Dangerous Operations)

- `sha.bash publish`: 此命令会发布软件包，除非用户在提示中明确指示，否则**禁止**执行。
- `git push`: **禁止**执行此命令。
- 任何删除多个文件的操作 (`rm -rf`) 都需要用户在提示中明确说明。