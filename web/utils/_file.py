from fastapi import UploadFile
from pathlib import Path
import os



from src.utils.config import get_config
from web.exceptions._file import UnsupportedFileFormat, LargeFile





# Configuration
ALLOWED_EXTENSIONS = get_config("uploads.allowed_extensions")
MAX_FILE_SIZE_BYTES = get_config("uploads.max_file_size_mb") * 1024 * 1024



def validate_file(file: UploadFile):
    """Validate file extension and size"""
    # Check file extension
    file_extension = Path(file.filename).suffix.lower().lstrip(".")
    if file_extension not in ALLOWED_EXTENSIONS: raise UnsupportedFileFormat
    
    # Check file size (prevent too large files)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_BYTES: raise LargeFile