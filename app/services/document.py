from pathlib import Path
from sqlalchemy.orm import Session
from app.core.file_storage import (
    UPLOAD_DIR,
    build_storage_filename,
    ensure_upload_dir,
)
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase


def create_document(
    db: Session,
    knowledge_base_id: int,
    original_filename: str,
    content: bytes,
) -> Document | None:
    knowledge_base = db.get(KnowledgeBase, knowledge_base_id)

    if knowledge_base is None:
        return None

    filename = Path(
        original_filename.replace("\\", "/")
    ).name

    if not filename:
        raise ValueError("文件名无效")

    storage_filename = build_storage_filename(filename)

    ensure_upload_dir()
    storage_file = UPLOAD_DIR / storage_filename
    storage_file.write_bytes(content)

    document = Document(
        knowledge_base_id=knowledge_base_id,
        filename=filename,
        storage_path=f"uploads/{storage_filename}",
        file_type=Path(filename).suffix.lower().lstrip("."),
        file_size=len(content),
        status="uploaded",
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        storage_file.unlink(missing_ok=True)
        raise

    return document
