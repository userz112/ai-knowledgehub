
from app.db.session import SessionLocal
from app.models.document import Document
from app.services.document_chunk import process_document_chunks


def main():
    db = SessionLocal()

    try:
        # 查询数据库中最新的一份文档
        document = (
            db.query(Document)
            .order_by(Document.id.desc())
            .first()
        )

        if document is None:
            print("数据库中没有文档，请先上传一份文件。")
            return

        print(f"正在处理文档：{document.id} - {document.filename}")

        count = process_document_chunks(db, document.id)

        print(f"处理成功！保存文本块数量：{count}")

    except Exception as e:
        print(f"处理失败：{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
