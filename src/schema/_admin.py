

from enum import Enum
import uuid

from pydantic import BaseModel
from datetime import datetime


class AdminUploadedDatasetType(str, Enum):
    PDF = "pdf"
    WORD = "docx"
    CSV = "csv"

