from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from app.services.knowledge_base import (
    create_knowledge_base as create_knowledge_base_service,
    list_knowledge_bases as list_knowledge_bases_service,
    get_knowledge_base as get_knowledge_base_service,
    update_knowledge_base as update_knowledge_base_service,
    delete_knowledge_base as delete_knowledge_base_service,
)
from fastapi import Depends, FastAPI, HTTPException, status, Response

app = FastAPI(title="KnowledgeHub AI")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def say_hello(name: str):
    return {"message": f"Hello, {name}"}

@app.post(
    "/knowledge-bases",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_base(
    data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
):
    return create_knowledge_base_service(db=db, data=data)


@app.get(
    "/knowledge-bases",
    response_model=list[KnowledgeBaseResponse],
)
def get_knowledge_bases(
    db: Session = Depends(get_db),
):
    return list_knowledge_bases_service(db=db)


@app.get(
    "/knowledge-bases/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base_detail(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
):
    knowledge_base = get_knowledge_base_service(
        db=db,
        knowledge_base_id=knowledge_base_id,
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    return knowledge_base


@app.put(
    "/knowledge-bases/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def update_knowledge_base_detail(
    knowledge_base_id: int,
    data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
):
    knowledge_base = update_knowledge_base_service(
        db=db,
        knowledge_base_id=knowledge_base_id,
        data=data,
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    return knowledge_base


@app.delete(
    "/knowledge-bases/{knowledge_base_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_base_detail(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
) -> Response:
    deleted = delete_knowledge_base_service(
        db=db,
        knowledge_base_id=knowledge_base_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

