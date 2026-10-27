from pydantic import BaseModel, ConfigDict


class DocumentProcessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: int
    status: str
    chunk_count: int
    message: str


