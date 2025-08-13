

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

import uuid


from src.operations._db_setup import get_sqlalchemy_db
from src.models._llm import ChatSession, RAGSystem
from src.schema._llm import CreateRAGSystemOutput, LLMType
from src.models._base_sqlalchemy import CURRENT_TIME
from src.schema._llm import AvailableRAGSystemsOutput
from src.utils.logger import app_logger


logger = app_logger.getChild("src.operations._llm")





class RAGSystemOperations:
    def __init__(self):
        self.session = get_sqlalchemy_db

    

    async def create(self, name: str, dataset_id: uuid.UUID):
        new_rag_system = RAGSystem(name=name, dataset_id=dataset_id)

        async with self.session() as session:
            session.add(new_rag_system)
            await session.commit()
        
        return CreateRAGSystemOutput(**new_rag_system.__dict__)


    async def delete(self, rag_system_id: uuid.UUID):
        query = sa.delete(RAGSystem).where(RAGSystem.id==rag_system_id)

        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()


    async def get(self, rag_system_id: uuid.UUID):
        query = sa.select(RAGSystem).where(RAGSystem.id==rag_system_id)

        async with self.session() as session:
            rag_system = await session.scalar(query)
        
        return rag_system

    async def list_available_rag_systems(self):
        query = sa.select(RAGSystem)
    
        async with self.session() as session:
            rag_systems = await session.scalars(query)
        rag_systems = rag_systems.all()
        if rag_systems: rag_systems = [AvailableRAGSystemsOutput(**i.__dict__) for i in rag_systems]
        return rag_systems

    async def change_name(self, rag_system_id: uuid.UUID, new_name: str):
        query = sa.update(RAGSystem)\
            .where(RAGSystem.id==rag_system_id).values(name=new_name)

        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()








class ChatSessionOperations:
    def __init__(self):
        self.session = get_sqlalchemy_db
    
    
    async def create(self, name: str, llm_type: LLMType, user_id: uuid.UUID):
        chat_session = ChatSession(
            user_id=user_id,
            name=name,
            llm_type=llm_type,
        )
        
        async with self.session() as session:
            session.add(chat_session)
            await session.commit()
        
        return chat_session
    
    
    
    async def delete_by_session_id(self, session_id: uuid.UUID):
        query = sa.delete(ChatSession).where(ChatSession.id==session_id)

        async with self.session() as session:
            _ = await session.execute(query)
            await session.commit()

    
    # async def delete_by_user_id(self, user_id: uuid.UUID):
    #     query = sa.delete(ChatSession).where(ChatSession.user_id==user_id)
        
    #     async with self.session() as session:
    #         _ = await session.execute(query)
    #         await session.commit()
        
    
    async def get_by_session_id(self, session_id: str):
        query = sa.select(ChatSession).where(ChatSession.id==session_id)
        
        async with self.session() as session:
            chat_session = await session.scalar(query)
            
        return chat_session
    
    
    
    async def list_by_user_id(self, user_id: uuid.UUID):
        query = sa.select(ChatSession).where(ChatSession.user_id==user_id)
    
        async with self.session() as session:
            chat_sessions = await session.scalars(query)
        
        return chat_sessions.all()
    
    
    
    async def update_last_active(self, session_id: uuid.UUID):
        query = sa.select(ChatSession).where(ChatSession.id==session_id)
    
        async with self.session() as session:
            chat_session = await session.scalar(query)
            if chat_session:
                chat_session.last_active = CURRENT_TIME()
                await session.commit()
    
    