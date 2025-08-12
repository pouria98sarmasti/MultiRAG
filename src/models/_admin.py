



from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, Boolean, Enum as SQLEnum, LargeBinary


import uuid
from enum import Enum


from src.models._base_sqlalchemy import Base, CURRENT_TIME
from src.schema._admin import AdminUploadedDatasetType





class AdminUploadedDatasetInfo(Base):
    __tablename__ = "admin_uploaded_dataset_info"
    __table_args__ = {'extend_existing': True}
    
    
    admin_id: Mapped[uuid.UUID] = mapped_column(index=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expertise: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_type: Mapped[AdminUploadedDatasetType] = mapped_column(SQLEnum(AdminUploadedDatasetType), nullable=False)
    # dataset_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    file_size_mb: Mapped[float] = mapped_column(nullable=False)
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime, default_factory=CURRENT_TIME)
    is_vectorized: Mapped[bool] = mapped_column(Boolean, default=False)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default_factory=uuid.uuid4)



class AdminUploadedDatasetContent(Base):
    __tablename__ = "admin_uploaded_dataset_content"
    __table_args__ = {'extend_existing': True}

    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("admin_uploaded_dataset_info.id", ondelete="CASCADE"), primary_key=True)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
