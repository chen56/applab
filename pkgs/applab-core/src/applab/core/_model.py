from typing import Any

from pydantic import BaseModel, SecretStr, field_serializer


# TODO : reactor move to storage.py , and rename to pydantic_ext.py
class AppLabBase(BaseModel):
    """AppLab 所有配置模型的基类"""

    @field_serializer("*", mode="plain", when_used="always")
    @classmethod
    def _serialize_secrets(cls, value: Any, info: Any):
        """
        允许明文序列化SecretStr字段
        """
        # 只要子模型继承了 AppLabBase，这个逻辑就会在每一层被触发
        if (isinstance(value, SecretStr)
                and info.context
                and info.context.get("show_secrets")):
            return value.get_secret_value()
        return value
