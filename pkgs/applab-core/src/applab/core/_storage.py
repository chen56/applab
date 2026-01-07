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
        atomic_save_text(self.path, doc.model_dump_json(indent=4))


# ---------------------------
# 文本版本
# ---------------------------
def atomic_save_text(
        path: Path,
        text: str,
        *,
        encoding: str = "utf-8",
        fsync: bool = True,
) -> None:
    """
    Atomically save text or JSON-serializable data to a file.

    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = _temp_file_path(path)

    with open(tmp, "w", encoding=encoding) as f:
        f.write(text)
        f.flush()
        if fsync:
            os.fsync(f.fileno())

    os.replace(tmp, path)


# ---------------------------
# 二进制版本
# ---------------------------
def atomic_save_bytes(
        path: Path,
        data: bytes,
        *,
        fsync: bool = True,
) -> None:
    """
    Atomically save binary data to a file.
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = _temp_file_path(path)

    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        if fsync:
            os.fsync(f.fileno())

    os.replace(tmp, path)


def _temp_file_path(path: Path) -> Path:
    """
    注意：
    1. 未使用tempfile.NamedTemporaryFile工具,因为它默认目录为/var/folders/.../T/tmpxxxx，而path可能在云盘，
    跨文件系统的os.replace不是原子操作。
    2. tmp文件即便失败也不用清理，下次重新覆盖和os.replace
    """
    return path.with_name(f".{path.name}.tmp")
