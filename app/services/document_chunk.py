from app.ai.vector_store import delete_document_chunks, upsert_chunks
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.ai.parser import extract_text_from_document
from app.ai.chunker import split_text


def process_document_chunks(
    db: Session,
    document_id: int,
) -> int:
    """提取文档正文、切分文本，并将文本块保存到数据库。"""

    # 1. 查询文档
    document = db.get(Document, document_id)

    if document is None:
        raise ValueError(f"文档不存在，document_id={document_id}")

    # 2. 提取文档正文
    text = extract_text_from_document(document)

    if not text.strip():
        raise ValueError("文档没有可用于分块的文本内容")

    # 3. 切分正文
    chunks = split_text(
        text,
        chunk_size=500,
        chunk_overlap=50,
    )

    if not chunks:
        raise ValueError("文档分块结果为空")

    try:
        # 4. 删除该文档以前生成的文本块
        # 避免重复处理时产生重复记录
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete(synchronize_session=False)

        # 5. 创建新的文本块记录
        chunk_records = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
            )
            for index, content in enumerate(chunks)
        ]

        db.add_all(chunk_records)
        document.status = "processed"

        # 6. 先提交新的 MySQL 文本块
        db.commit()

        # 7. 删除该文档在 Chroma 中的旧向量
        delete_document_chunks(document_id)

        # 8. 为新的文本块生成向量并写入 Chroma
        upsert_chunks(chunk_records)

        return len(chunk_records)

    except Exception:
        db.rollback()
        raise
