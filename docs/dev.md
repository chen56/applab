# 开发

## 项目初始化

## 已采纳

- 验证及模型定义: [pydantic](https://pydantic.dev)
- 日志:
- 命令cli: [cyclopts](https://github.com/BrianPugh/cyclopts)
- py项目管理/build: [uv](https://github.com/astral-sh/uv)
- 类型注解
  - 类型注解元数据: [annotated-types](https://github.com/annotated-types/annotated-types)
    - Python 3.9+ 引入的 typing.Annotated 仅支持「类型 + 任意元数据」的基础形式（如 Annotated[int, "positive"]）；而 annotated_types 则提供了标准化、可复用的元数据类，让类型注解的约束更清晰、可机器解析（比如被 Pydantic、FastAPI 等库识别）。

## 依赖候选

### 可观测性

- https://github.com/pydantic/logfire
