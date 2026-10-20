from pathlib import Path
from uuid import uuid4

from app.core.config import BASE_DIR


UPLOAD_DIR = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {".txt", ".pdf"}


def ensure_upload_dir() -> None:
    """确保文件上传目录存在。"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def build_storage_filename(original_filename: str) -> str:
    """生成随机且带有原始扩展名的存储文件名。"""
    suffix = Path(original_filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("仅支持上传 .txt 和 .pdf 文件")

    return f"{uuid4().hex}{suffix}"
