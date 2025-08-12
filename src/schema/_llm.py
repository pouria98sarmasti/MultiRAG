import uuid
from enum import Enum
from pydantic import BaseModel




class LLMType(str, Enum):
    """Enum for different LLM types in the system."""
    SIMPLE = "simple"
    RAG = "rag"
    USER_RAG = "user_rag"

class AvailableRAGSystemsOutput(BaseModel):
    id: uuid.UUID
    name: str
    dataset_id: uuid.UUID


class CreateRAGSystemOutput(BaseModel):
    name: str
    id: uuid.UUID
    dataset_id: uuid.UUID