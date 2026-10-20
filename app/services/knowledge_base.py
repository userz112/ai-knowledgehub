from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
from sqlalchemy import select


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


def list_knowledge_bases(db: Session) -> list[KnowledgeBase]:
    statement = select(KnowledgeBase).order_by(
        KnowledgeBase.id.desc()
    )
    return list(db.scalars(statement).all())

def get_knowledge_base(
    db: Session,
    knowledge_base_id: int,
) -> KnowledgeBase | None:
    return db.get(KnowledgeBase, knowledge_base_id)

def update_knowledge_base(
    db: Session,
    knowledge_base_id: int,
    data: KnowledgeBaseUpdate,
) -> KnowledgeBase | None:
    knowledge_base = db.get(KnowledgeBase, knowledge_base_id)

    if knowledge_base is None:
        return None

    try:
        knowledge_base.name = data.name
        knowledge_base.description = data.description

        db.commit()
        db.refresh(knowledge_base)
    except Exception:
        db.rollback()
        raise

    return knowledge_base

def delete_knowledge_base(
    db: Session,
    knowledge_base_id: int,
) -> bool:
    knowledge_base = db.get(KnowledgeBase, knowledge_base_id)

    if knowledge_base is None:
        return False

    try:
        db.delete(knowledge_base)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True
