from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

import uuid


from src.models._llm import RAGSystem
from src.models._user import User
from src.models._association_tables import UserRAGSystemJunction
from src.operations._db_setup import get_sqlalchemy_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)




class UserRAGSystemJunctionOperations:
    def __init__(self) -> None:
        self.session = get_sqlalchemy_db
    

    async def add_user_access(self, user_id: uuid.UUID, rag_system_id: uuid.UUID):
        new_access = UserRAGSystemJunction(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        async with self.session() as session:
            session.add(new_access)
            await session.commit()
        
        return new_access


    async def remove_user_access(self, user_id: uuid.UUID, rag_system_id: uuid.UUID):
        query = sa.delete(UserRAGSystemJunction)\
            .where(
                UserRAGSystemJunction.user_id==user_id,
                UserRAGSystemJunction.rag_system_id==rag_system_id,
            )
        
        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()


    async def list_users_by_rag_system_id(self, rag_system_id: uuid.UUID):
        query = sa.select(RAGSystem).where(RAGSystem.id==rag_system_id)
        
        async with self.session() as session:
            rag_system_data = await session.scalar(query)

        users_id = [i.user_id for i in rag_system_data.users]
        
        return users_id

    async def list_rag_systems_by_user_id(self, user_id: uuid.UUID):
        query = sa.select(User).where(User.id==user_id)
        
        async with self.session() as session:
            user_data = await session.scalar(query)

        rag_systems_id = [i.rag_system_id for i in user_data.rag_systems]

        return rag_systems_id