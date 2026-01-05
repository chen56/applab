import os
import pathlib
from pathlib import Path

from pydantic import BaseModel


class JsonStorage[T: BaseModel]:
    def __init__(self, path: Path, model: type[T]):
        self.path = path
        self.model = model

    def load(self) -> T:
        if not self.path.exists():
            # 要求无参构造器
            return self.model()

        json_string = pathlib.Path(self.path).read_text(encoding="utf-8")
        return self.model.model_validate_json(json_string)

    def save(self, doc: T):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        tmp = self.path.with_suffix(".json.tmp")

        # 1. 写临时文件
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(doc.model_dump_json(indent=4))
            f.flush()
            os.fsync(f.fileno())

        # 2. 原子替换
        os.replace(tmp, self.path)
