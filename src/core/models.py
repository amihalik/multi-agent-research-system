from datetime import datetime
from sqlmodel import SQLModel, Field, JSON

class Query(SQLModel, table=True):
    id: str = Field(primary_key=True)
    prompt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRun(SQLModel, table=True):
    id: str = Field(primary_key=True)
    query_id: str
    role: str                # "lead" / "sub" / "citation"
    status: str              # pending / running / done / error
    tokens: int | None = None
    result: JSON | None = None
