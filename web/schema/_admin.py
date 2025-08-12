from pydantic import BaseModel
import uuid




class UserCreateInput(BaseModel):
    username: str
    user_id: uuid.UUID


class ListAllDatasetsInput(BaseModel):
    dataset_id: uuid.UUID
    vectorize_status: bool | None = None


class CreateRAGSystemInput(BaseModel):
    rag_name: str
    dataset_id: uuid.UUID


class ChangeNameRAGSystemInput(BaseModel):
    rag_system_id: uuid.UUID
    new_name: str



class UserAccessInput(BaseModel):
    user_id: uuid.UUID
    rag_system_id: uuid.UUID


class GetUserOutput(BaseModel):
    username: str
    id: uuid.UUID



class GetRAGSystemOutput(BaseModel):
    name: str
    id: uuid.UUID
    dataset_id: uuid.UUID