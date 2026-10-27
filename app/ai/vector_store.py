from functools import lru_cache
from app.models.document_chunk import DocumentChunk
from app.ai.embedding import encode_texts
import chromadb
from app.core.config import BASE_DIR

CHROMA_DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "knowledgehub_chunks_v4"

@lru_cache(maxsize=1)
def get_chroma_collection():
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
    )

    return client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "hnsw:batch_size": 100,
        "hnsw:sync_threshold": 100,
        },
    )

def upsert_chunks(chunks: list[DocumentChunk]) -> int:
    if not chunks:
        return 0

    ids = [
        f"doc-{chunk.document_id}-chunk-{chunk.chunk_index}"
        for chunk in chunks
    ]       # 每个 chunk 的 id 转成字符串
    documents = [chunk.content for chunk in chunks]     # 每个 chunk 的 content    
    embeddings = encode_texts(documents)         # 对 documents 批量调用 encode_texts
    metadatas = [
        {
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "chunk_id": chunk.id,
        }
        for chunk in chunks
    ]       # 每个元素保存 document_id 和 chunk_index

    collection = get_chroma_collection()
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)

def delete_document_chunks(document_id: int) -> None:
    collection = get_chroma_collection()
    collection.delete(
        where={"document_id": document_id},
    )

def search_chunks(
    query: str,
    n_results: int = 5,
    where: dict | None = None,
) -> dict:
    if not query.strip():
        raise ValueError("查询内容不能为空")

    if n_results <= 0:
        raise ValueError("n_results 必须大于 0")

    query_vector = encode_texts([query])[0]
    collection = get_chroma_collection()

    query_kwargs = {
        "query_embeddings": [query_vector],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }

    if where is not None:
        query_kwargs["where"] = where

    return collection.query(**query_kwargs)
