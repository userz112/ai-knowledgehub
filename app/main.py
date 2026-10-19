from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="KnowledgeHub AI")

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ''

@app.post("/knowledge-bases")
def create_knowledge_base(data: KnowledgeBaseCreate):
    return {
        "message": "知识库创建成功",
        "data": data
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def say_hello(name: str):
    return {"message": f"Hello, {name}"}