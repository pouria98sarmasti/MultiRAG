from fastapi import APIRouter, Body

import uuid

from src.operations._admin import AdminUploadedDatasetContentOperations, AdminUploadedDatasetInfoOperations
from src.operations._association_operations import UserRAGSystemJunctionOperations
from src.operations._chat_history import chat_history_service
from src.operations._document_hadling import document_service
from src.operations._llm import RAGSystemOperations
from src.operations._user import UserOperations
from src.operations._vector_db import vector_db_service
from web.schema._admin import UserAccessInput, ChangeNameRAGSystemInput, CreateRAGSystemInput, GetRAGSystemOutput, GetUserOutput, ListAllDatasetsInput, UserCreateInput






admin_router = APIRouter()





#### user managements

@admin_router.post("/user", tags=["Admin-User Management"])
async def create_user(data: UserCreateInput = Body()):
    user = await UserOperations().create(
        username=data.username,
        user_id=data.user_id,
    )
    await chat_history_service.create_user_chat_history(user_id=data.user_id)

    return user

@admin_router.get("/user", tags=["Admin-User Management"])
async def list_all_users():
    users = await UserOperations().list_all_users()
    return users


@admin_router.delete("/user", tags=["Admin-User Management"])
async def delete_user(user_id: uuid.UUID):
    await UserOperations().delete(user_id=user_id)
    await chat_history_service.delete_user_chat_history(user_id=user_id)
    return {"message": "User successfuly deleted"}





#### dataset managements



# async def upload_dataset():
#     pass

@admin_router.post("/dataset", tags=["Admin-Dataset Management"])
async def vectorize_dataset_and_create_rag_system(data: CreateRAGSystemInput = Body()):
    dataset_info = await AdminUploadedDatasetInfoOperations().get_by_dataset_id(dataset_id=data.dataset_id)
    dataset_content = await AdminUploadedDatasetContentOperations().get_content(dataset_id=data.dataset_id)
    documents = document_service.to_documents(
        file_format=dataset_info.dataset_type,
        file_content=dataset_content,
    )
    await vector_db_service.add_documents(
        documents=documents,
        dataset_id=data.dataset_id,
    )
    _ = await AdminUploadedDatasetInfoOperations().change_vectorize_status(
        dataset_id=data.dataset_id,
        is_vectorized=True,
    )
    rag_system = await RAGSystemOperations().create(
        name=data.rag_name,
        dataset_id=data.dataset_id,
    )
    return rag_system



# async def add_complementary_dataset():
#     pass

@admin_router.get("/dataset", tags=["Admin-Dataset Management"])
async def list_all_datasets(is_vectorized: bool | None = None):
    datasets = await AdminUploadedDatasetInfoOperations().list_by_vectorize_status(is_vectorized=is_vectorized)
    return datasets


@admin_router.delete("/dataset", tags=["Admin-Dataset Management"])
async def delete_dataset_and_rag_system(dataset_id: uuid.UUID):
    await vector_db_service.delete_vectore_table(dataset_id=dataset_id)
    await AdminUploadedDatasetInfoOperations().delete(dataset_id=dataset_id)
    return {"message": "Dataset successfully deleted."}


# async def download_dataset():
#     pass






#### rag systems management

@admin_router.get("/models", tags=["Admin-RAG System Management"])
async def list_available_models():
    rag_systems = await RAGSystemOperations().list_available_rag_systems()
    available_models = {
        "simple": "simple",
        "user_rag": "user_rag",
        "rag": rag_systems,
    }

    return available_models

@admin_router.get("/rag_system", tags=["Admin-RAG System Management"])
async def list_available_rag_systems():
    rag_systems = await RAGSystemOperations().list_available_rag_systems()
    return rag_systems



@admin_router.put("/rag_system", tags=["Admin-RAG System Management"])
async def change_name_of_a_rag_system(data: ChangeNameRAGSystemInput = Body()):
    await RAGSystemOperations().change_name(
        rag_system_id=data.rag_system_id,
        new_name=data.new_name,
    )
    return {"message": f"Name of RAG system changed to {data.new_name} successfully"}
    



#### rag system access management


@admin_router.post("/rag_access", tags=["Admin-RAG System Access Management"])
async def add_user_access(data: UserAccessInput = Body()):
    _ = await UserRAGSystemJunctionOperations().add_user_access(
        user_id=data.user_id,
        rag_system_id=data.rag_system_id,
    )
    return {"message": "Access gave successfully."}

@admin_router.get("/rag_access/users", tags=["Admin-RAG System Access Management"])
async def list_users_by_rag_system_id(rag_system_id: uuid.UUID):
    users_id = await UserRAGSystemJunctionOperations().list_users_by_rag_system_id(rag_system_id=rag_system_id)
    users = []
    if users_id:
        users = [await UserOperations().get(id) for id in users_id]
        users = [GetUserOutput(**i.__dict__) for i in users]

    return users


@admin_router.get("/rag_access/rag_systems", tags=["Admin-RAG System Access Management"])
async def list_rag_systems_by_user_id(user_id: uuid.UUID):
    rag_systems_id = await UserRAGSystemJunctionOperations().list_rag_systems_by_user_id(user_id=user_id)
    rag_systems = []
    if rag_systems_id:
        rag_systems = [await RAGSystemOperations().get(id) for id in rag_systems_id]
        rag_systems = [GetRAGSystemOutput(**i.__dict__) for i in rag_systems]

    return rag_systems




@admin_router.delete("/rag_access", tags=["Admin-RAG System Access Management"])
async def remove_user_access(data: UserAccessInput = Body()):
    await UserRAGSystemJunctionOperations().remove_user_access(
        user_id=data.user_id,
        rag_system_id=data.rag_system_id,
    )
    return {"message": "Access removed successfully."}

