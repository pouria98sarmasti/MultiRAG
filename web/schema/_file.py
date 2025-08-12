from pydantic import BaseModel
import uuid

class UploadFileInput(BaseModel):
    file_name: str
    expertise: str
    admin_id: uuid.UUID

class DownloadFileInput(BaseModel):
    dataset_id: uuid.UUID