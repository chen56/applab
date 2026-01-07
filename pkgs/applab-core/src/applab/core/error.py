"""

AppError
│
├── CheckError
│   └─ Invariant / assumption violated
│   （替代assert的断言/不变量检查，bug, 程序问题）
│
├── BizError
│   ├─ NotLoggedIn
│   ├─ PermissionDenied
│   ├─ QuotaExceeded
│   └─ InvalidWorkflow
│   （业务规则 / 流程失败, 用户操作/状态问题）
│
└── 未分类其他异常
    ├─ NetworkDisconnected
    └─ DeviceUnavailable
    （究竟是系统问题还是什么问题需要程序边界解释器自行动态解释）

"""


# reference:
# https://docs.python.org/zh-cn/3.14/library/exceptions.html
# https://docs.python.org/zh-cn/3.14/tutorial/errors.html
class ApplabError(Exception):
    """Base class for all application-level errors."""

    user_visible: bool = False
    retryable: bool = False


# ---------- Business ----------


class BizError(ApplabError):
    """
    业务异常: 可预料的业务流程，非故障，比如:
    - 用户可感知错误: 表单、权限、操作超限
    - 业务流程异常: 状态机异常、业务规则冲突

    处理事项：
    - 应用于 CLI/GUI 的提示
    - 不应打印 traceback 到终端
    - 可携带结构化信息（字段名、错误码）
    """

    pass


# ---------- Check / Invariant ----------


class CheckError(AssertionError):
    """
    Invariant Check Error, like `assert`, but assert not raise error when running in optimized mode

    ref: <https://discuss.python.org/t/stop-ignoring-asserts-when-running-in-optimized-mode>
    """

    user_visible = False
    retryable = False


def check(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)
