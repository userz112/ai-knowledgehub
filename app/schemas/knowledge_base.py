from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    created_at: datetime

class KnowledgeBaseUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str

