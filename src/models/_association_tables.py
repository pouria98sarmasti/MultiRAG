from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

import uuid


from src.models._base_sqlalchemy import Base



class UserRAGSystemJunction(Base):
    __tablename__ = "user_rag_system_junction"
    __table_args__ = {'extend_existing': True}

    # composite primary_key
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    rag_system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('rag_system.id', ondelete="CASCADE"), primary_key=True)