import os
from dotenv import load_dotenv
from openai import OpenAI
from app.ai.vector_store import search_chunks
from app.schemas.chat import ChatResponse
from sqlalchemy.orm import Session
from app.models.document import Document
load_dotenv(".env")


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

def ask_question(
    db: Session,
    question: str,
    knowledge_base_id: int,
) -> ChatResponse:
    document_ids = [
        document_id
        for (document_id,) in db.query(Document.id)
        .filter(Document.knowledge_base_id == knowledge_base_id)
        .all()
    ]

    if not document_ids:
        return ChatResponse(
            answer="No documents found in this knowledge base.",
            source_ids=[],
            source_metadata=[],
        )

    search_result = search_chunks(
        question,
        n_results=3,
        where={"document_id": {"$in": document_ids}},
    )
    documents = search_result["documents"][0]
    context = "\n\n".join(documents)
    if not context:
        return ChatResponse(
            answer="No relevant content found.",
            source_ids=[],
            source_metadata=[],
        )
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer only from the provided knowledge base content. "
                    "If the answer is not in the content, say that it is not found."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Knowledge base content:\n{context}\n\n"
                    f"Question:\n{question}"
                ),
            },
        ],
        stream=False,
    )
    return ChatResponse(
        answer=response.choices[0].message.content,
        source_ids=search_result["ids"][0],
        source_metadata=search_result["metadatas"][0],
    )

