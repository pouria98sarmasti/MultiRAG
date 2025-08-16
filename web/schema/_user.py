from pydantic import BaseModel
import uuid


from src.schema._llm import LLMType


class CreateChatSessionInput(BaseModel):
    name: str
    llm_type: LLMType
    user_id: uuid.UUID
    rag_system_id: uuid.UUID | None = None


class ReturnChatHistoryInput(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID


class DeleteChatSessionInput(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID


class ChatInput(BaseModel):
    llm_type: LLMType
    user_id: uuid.UUID
    session_id: uuid.UUID
    rag_system_id: uuid.UUID | None = None
    user_prompt: str