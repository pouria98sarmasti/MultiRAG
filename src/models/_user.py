



from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Boolean, Enum as SQLEnum, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship


import uuid
from enum import Enum


from src.models._base_sqlalchemy import Base, CURRENT_TIME
from src.models._llm import ChatSession
from src.models._association_tables import UserRAGSystemJunction



class UserUploadedDatasetType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    CSV = "csv"


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    # 1-N relationship with chat_session table
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", 
        lazy="selectin", 
        init=False, 
        collection_class=list,
        cascade="all, delete-orphan", # delete all session when user is deleted
    )
    rag_systems: Mapped[list["UserRAGSystemJunction"]] = relationship(
        "UserRAGSystemJunction",
        init=False,
        lazy="selectin",
        collection_class=list,
        cascade="all, delete-orphan",
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, nullable=False)



class UserUploadedDataset(Base):
    __tablename__ = "user_upload"
    __table_args__ = {'extend_existing': True}
    
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    dataset_type: Mapped[UserUploadedDatasetType] = mapped_column(SQLEnum(UserUploadedDatasetType), nullable=False)
    dataset_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime, default_factory=CURRENT_TIME)
    is_vectorized: Mapped[bool] = mapped_column(Boolean, default=True)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default_factory=uuid.uuid4)
    