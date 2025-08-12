from fastapi import APIRouter, Body

import uuid

from fastapi.responses import StreamingResponse

from src.llm._llm_factory import create_llm
from src.operations._chat_history import chat_history_service
from src.operations._llm import ChatSessionOperations, RAGSystemOperations
from web.schema._user import ChatInput, CreateChatSessionInput, DeleteChatSessionInput, ReturnChatHistoryInput






user_router = APIRouter(tags=["User"])







@user_router.get("/models")
async def list_available_models():
    rag_systems = await RAGSystemOperations().list_available_rag_systems()
    available_models = {
        "simple": "simple",
        "user_rag": "user_rag",
        "rag": rag_systems,
    }

    return available_models

@user_router.post("/chat/create")
async def create_chat_session(data: CreateChatSessionInput = Body()):
    chat_session = await ChatSessionOperations().create(
        name=data.name,
        llm_type=data.llm_type,
        user_id=data.user_id,
    )

    return chat_session


@user_router.get("/chat")
async def list_chat_sessions(user_id: uuid.UUID):
    chat_sessions = await ChatSessionOperations().list_by_user_id(user_id=user_id)
    return chat_sessions


@user_router.post("/chat/history")
async def return_history_for_a_chat_session(data: ReturnChatHistoryInput = Body()):
    chat_history = await chat_history_service.get_session_messages(
        user_id=data.user_id,
        session_id=data.session_id,
    )
    return chat_history


@user_router.delete("/chat")
async def delete_chat_session(data: DeleteChatSessionInput = Body()):
    await chat_history_service.delete_session_history(
        user_id=data.user_id,
        session_id=data.session_id,
    )
    await ChatSessionOperations().delete_by_session_id(session_id=data.session_id)

    return {"message": f"session {data.session_id} successfully deleted."}
    

@user_router.post("/chat")
async def chat(data: ChatInput = Body()):
    llm = await create_llm(
        llm_type=data.llm_type,
        user_id=data.user_id,
        session_id=data.session_id,
        dataset_id=data.dataset_id,
    )

    return StreamingResponse(
        content=llm.generate_chat_response(user_query=data.user_prompt),
        media_type="application/x-ndjson; charset=utf-8",
    )


