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
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, status, Response, UploadFile, File
from app.schemas.document import DocumentResponse
from app.services.document import create_document as create_document_service
from app.models.document import Document
from app.services.document_chunk import process_document_chunks
from app.schemas.document_process import DocumentProcessResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ask_question
from app.models.knowledge_base import KnowledgeBase


app = FastAPI(title="KnowledgeHub AI")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MiB

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


@app.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    knowledge_base_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供文件名",
            )

        original_filename = Path(
            file.filename.replace("\\", "/")
        ).name

        content = await file.read(MAX_UPLOAD_SIZE + 1)

        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="文件不能超过 10 MiB",
            )

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能上传空文件",
            )

        try:
            document = create_document_service(
                db=db,
                knowledge_base_id=knowledge_base_id,
                original_filename=original_filename,
                content=content,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器保存文件失败",
            ) from exc

    finally:
        await file.close()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    return document


@app.post(
    "/documents/{document_id}/process",
    response_model=DocumentProcessResponse,
)
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    # 1. 检查文档是否存在
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="文档不存在",
        )

    try:
        # 2. 执行正文提取、文本分块和数据库保存
        chunk_count = process_document_chunks(
            db=db,
            document_id=document_id,
        )

        return DocumentProcessResponse(
            document_id=document_id,
            status="processed",
            chunk_count=chunk_count,
            message="文档处理成功",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="文档处理失败，请检查服务端日志",
        ) from exc

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
):
    knowledge_base = db.get(KnowledgeBase, data.knowledge_base_id)
    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="知识库不存在",
        )
    try:
        return ask_question(
            db=db,
            question=data.question,
            knowledge_base_id=data.knowledge_base_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    

