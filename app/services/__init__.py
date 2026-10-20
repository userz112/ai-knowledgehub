from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate


def create_knowledge_base(
    db: Session,
    data: KnowledgeBaseCreate,
) -> KnowledgeBase:
    knowledge_base = KnowledgeBase(
        name=data.name,
        description=data.description,
    )

    try:
        db.add(knowledge_base)
        db.commit()
        db.refresh(knowledge_base)
    except Exception:
        db.rollback()
        raise

    return knowledge_base