
import uuid
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


from src.operations._db_setup import get_psycopg_db, drop_table
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ChatHistoryService:
    def __init__(self) -> None:
        self.connection = get_psycopg_db
    
    def _get_table_name(self, user_id: uuid.UUID) -> str:
        return f"chat_histories_user_id_{str(user_id).replace('-', '_')}"
    
    
    async def create_user_chat_history(self, user_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        async with self.connection() as conn:
            await PostgresChatMessageHistory.acreate_tables(conn, TABLE_NAME)
            
    
    async def delete_user_chat_history(self, user_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        await drop_table(TABLE_NAME)
    
    async def delete_session_history(self, user_id: uuid.UUID, session_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        async with self.connection() as conn:
            session_history = PostgresChatMessageHistory(
                TABLE_NAME,  # Optional custom table
                str(session_id),
                async_connection=conn,
            )
            await session_history.aclear()
    
    async def get_session_messages(self, user_id: uuid.UUID, session_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        async with self.connection() as conn:
            session_history = PostgresChatMessageHistory(
                TABLE_NAME,  # Optional custom table
                str(session_id),
                async_connection=conn,
            )
            messages = await session_history.aget_messages()
            return messages
    
    async def add_user_message(self, message:str, user_id: uuid.UUID, session_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        async with self.connection() as conn:
            session_history = PostgresChatMessageHistory(
                TABLE_NAME,  # Optional custom table
                str(session_id),
                async_connection=conn,
            )
            user_message = HumanMessage(content=message)
            await session_history.aadd_messages([user_message])
    
    async def add_ai_message(self, message:str, user_id: uuid.UUID, session_id: uuid.UUID):
        TABLE_NAME = self._get_table_name(user_id=user_id)
        
        async with self.connection() as conn:
            session_history = PostgresChatMessageHistory(
                TABLE_NAME,  # Optional custom table
                str(session_id),
                async_connection=conn,
            )
            ai_message = AIMessage(content=message)
            await session_history.aadd_messages([ai_message])




chat_history_service = ChatHistoryService()