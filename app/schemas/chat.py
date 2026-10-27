from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    knowledge_base_id: int

class ChatResponse(BaseModel):
    answer: str
    source_ids: list[str]
    source_metadata: list[dict]
