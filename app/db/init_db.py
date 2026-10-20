from app.db.base import Base
from app.db.session import engine
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document

def init_db():
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")


if __name__ == "__main__":
    init_db()
