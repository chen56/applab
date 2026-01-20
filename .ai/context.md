# Applab Project Context

## Overview
Applab is a cloud application deployment tool designed with a plugin architecture to support multiple cloud vendors (e.g., Tencent Cloud).

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
```text
applab/
├── pkgs/
│   ├── applab-cli/          # CLI Entry & UX
│   ├── applab-core/         # Core Logic (Auth, Storage, Models)
│   └── applab-vendor-*/     # Vendor Adapters (e.g., tencentcloud)
├── src/
│   └── applab/              # Namespace Root
├── .ai/                     # AI Context & Rules
└── pyproject.toml           # Workspace Config
```

## Modules
- **applab-core**: Universal classes, assertions, auth management, storage abstraction.
- **applab-cli**: CLI logic, command parsing (Cyclopts), console output.
- **applab-vendor-***: Cloud provider implementations (Auth, Resource Management).

## Development
### Environment
- **Setup**: `uv sync` (Syncs entire workspace)
- **Test**: `pytest` or `./sha test`
- **Build**: `uv build` or `./sha build`

### Standards
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/).
- **Code Style**: Ruff, NumPy docstrings, 120 line length.

## Authentication
| Vendor | ID Credential | Secret Credential | Key Params |
| :--- | :--- | :--- | :--- |
| AWS | access_key_id | secret_access_key | region_name |
| Tencent | secret_id | secret_key | - |
| Aliyun | access_key_id | access_key_secret | - |
| Azure | client_id | client_secret | tenant_id, subscription_id |
| GCP | client_email | private_key | project_id |

## References
- **GitHub Rules**: [See Rules](rules/github.md) (Load via `read_file` if needed).