
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Body, Depends, UploadFile, File
from fastapi.responses import FileResponse

from pydantic import ValidationError



from src.operations._admin import AdminUploadedDatasetContentOperations, AdminUploadedDatasetInfoOperations
from src.utils.config import get_config
from web.exceptions._file import FileNotFound, SavingFile, ValidationErrorHTTP
from web.schema._file import DownloadFileInput, UploadFileInput
from web.utils._file import validate_file



file_router = APIRouter(tags=["Admin-Dataset Management"])




# @file_router.post("/")



# Configuration
UPLOAD_DIR = get_config("uploads.storage_path")



## can not use UploadFile with Body() 
@file_router.post("/")
async def upload_file(file: UploadFile = File(...), data: UploadFileInput = Depends()):
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    validate_file(file)
    file_path = Path(UPLOAD_DIR + "/" + file.filename)

    try:
        # Save file in local storage (efficient for large files)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        with open(file_path, "rb") as f:
            content = f.read()
        file_size_mb = f"{os.path.getsize(file_path) / (1024*1024):.2f}"
        file_size_mb = float(file_size_mb)
        dataset = await AdminUploadedDatasetInfoOperations().create(
            name=data.file_name,
            dataset_type=file_path.suffix.lstrip("."),
            expertise=data.expertise,
            file_size_mb=file_size_mb,
            admin_id=data.admin_id
        )
        _ = await AdminUploadedDatasetContentOperations().create(
            dataset_id=dataset.id,
            content=content,
        )
    except ValidationError as e: raise ValidationErrorHTTP(e.json(indent=2))
    except Exception: raise SavingFile
    
    try:
        return dataset
    finally:
        file.file.close()
        file_path.unlink()


## get methods can not have body
@file_router.get("/")
async def download_file(data: DownloadFileInput = Depends()):
    # save file in disk (efficient handling large files)
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True) # for first time app downlaod
    shutil.rmtree(UPLOAD_DIR)
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    try:

        dataset_info = await AdminUploadedDatasetInfoOperations().get_by_dataset_id(dataset_id=data.dataset_id)
        dataset_content = await AdminUploadedDatasetContentOperations().get_content(dataset_id=data.dataset_id)
        dataset_name = dataset_info.dataset_name
        dataset_extension = dataset_info.dataset_type.value

    except Exception: raise FileNotFound

    try:
        file_name = dataset_name + "." + dataset_extension
        file_path = Path(UPLOAD_DIR + "/" + file_name)
        with open(file_path, "wb") as f:
            _ = f.write(dataset_content)
    except ValidationError as e: raise ValidationErrorHTTP(e.json(indent=2))
    except Exception: raise SavingFile



    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )