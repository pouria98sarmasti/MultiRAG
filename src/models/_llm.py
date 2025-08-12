


from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship

import uuid
from enum import Enum


from src.models._base_sqlalchemy import Base, CURRENT_TIME
from src.models._association_tables import UserRAGSystemJunction
from src.schema._llm import LLMType




class RAGSystem(Base):
    __tablename__ = "rag_system"
    __table_args__ = {'extend_existing': True}

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=True)
    dataset_id:  Mapped[uuid.UUID] = mapped_column(ForeignKey("admin_uploaded_dataset_info.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    # 1-N relationship to the association object (M-N relationship with user table)
    users: Mapped[list["UserRAGSystemJunction"]] = relationship(
        "UserRAGSystemJunction",
        lazy="selectin",
        init=False,
        collection_class=list,
        cascade="all, delete-orphan",
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, nullable=False, default_factory=uuid.uuid4)



class ChatSession(Base):
    __tablename__ = "chat_session"
    __table_args__ = {'extend_existing': True}
    
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    llm_type: Mapped[LLMType] = mapped_column(SQLEnum(LLMType), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default_factory=CURRENT_TIME)
    last_active: Mapped[DateTime] = mapped_column(DateTime, default_factory=CURRENT_TIME)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, nullable=False, default_factory=uuid.uuid4)

