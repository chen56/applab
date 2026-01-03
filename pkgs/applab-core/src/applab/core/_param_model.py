from pydantic import BaseModel


class BaseParamModel(BaseModel):
    model_config = {
        "kw_only": True
    }


class UIField(BaseModel):
    model_config = {"kw_only": True}  # 强制所有字段为关键字参数


class TextField(UIField):
    label: str
    # error:Fields with a default value must come after any fields without a default.
    type: str
    help: str = ""
