from app.db.session import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.ai.vector_store import get_chroma_collection, upsert_chunks

BATCH_SIZE = 100

def main():
    db = SessionLocal()
    last_id = 0
    processed = 0

    try:
        total = db.query(DocumentChunk).count()

        while True:
            chunks = (
                db.query(DocumentChunk)
                .filter(DocumentChunk.id > last_id)
                .order_by(DocumentChunk.id)
                .limit(BATCH_SIZE)
                .all()
            )

            if not chunks:
                break

            processed += upsert_chunks(chunks)
            last_id = chunks[-1].id

            print(f"已处理：{processed}/{total}，当前最大 ID：{last_id}")

        print(f"完成。Chroma 向量数量：{get_chroma_collection().count()}")

    finally:
        db.close()

if __name__ == "__main__":
    main()