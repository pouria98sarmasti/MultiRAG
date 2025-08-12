from fastapi import HTTPException, status


from src.utils.config import get_config


# Configuration
ALLOWED_EXTENSIONS = get_config("uploads.allowed_extensions")
MAX_FILE_SIZE_MB = get_config("uploads.max_file_size_mb")


class UnsupportedFileFormat(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"



class LargeFile(HTTPException):
    def __init__(self):
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"



class ValidationErrorHTTP(HTTPException):
    def __init__(self, error: str):
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        detail= error


class SavingFile(HTTPException):
    def __init__(self):
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        detail= "Error saving file"


class FileNotFound(HTTPException):
    def __init__(self):
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found error."