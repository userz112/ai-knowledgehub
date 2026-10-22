import pymupdf
from app.core.config import BASE_DIR
from app.core.file_storage import UPLOAD_DIR
from app.models.document import Document


def extract_text_from_document(document: Document) -> str:
    """从已保存的 TXT 或 PDF 文档中提取文本。"""

    file_path = (BASE_DIR / document.storage_path).resolve()
    upload_root = UPLOAD_DIR.resolve()

    # 确保读取的文件位于 uploads 目录内
    try:
        file_path.relative_to(upload_root)
    except ValueError as exc:
        raise ValueError("文件路径不在允许的存储目录内") from exc

    if not file_path.is_file():
        raise FileNotFoundError(
            f"文档文件不存在：{document.id}"
        )

    if document.file_type == "txt":
        raw_content = file_path.read_bytes()

        try:
            text = raw_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw_content.decode("gb18030")

        return text.strip()

    if document.file_type == "pdf":
        with pymupdf.open(file_path) as pdf:
            pages = [
                page.get_text("text")
                for page in pdf
            ]

        return "\n".join(pages).strip()

    raise ValueError(
        f"暂不支持的文件类型：{document.file_type}"
    )
