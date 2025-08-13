



import uuid
import re

from langchain_postgres import PGVectorStore
from langchain_postgres.v2.indexes import HNSWIndex
from langchain_postgres import Column

from langchain_core.documents import Document

from sqlalchemy.exc import ProgrammingError

from typing import List


from src.operations._db_setup import get_pg_engine, drop_table
from src.llm._llm_setup import get_embedding_model
from src.utils.config import get_config
from src.utils.logger import app_logger




logger = app_logger.getChild("src.operations._vector_db")



class VectorDbService:
    
    def __init__(self) -> None:
        self.engine = get_pg_engine()
        
        self.embedding = get_embedding_model()
        self.VECTOR_SIZE = get_config("llm.embedding.vector_size")
        
        self.search_type = get_config("rag.search_type")
        self.k_retrieval = get_config("rag.k_retrieval")
        self.score_threshold = get_config("rag.score_threshold")
        
    
    
    def _get_table_name(self, dataset_id: uuid.UUID) -> str:
        return f"vector_db_dataset_id_{str(dataset_id).replace('-', '_')}"
    
    # def _get_dataset_id(self, table_name: str) -> str:
    #     pass
    
    async def _init_vector_table(self, dataset_id: uuid.UUID) -> None:
        TABLE_NAME = self._get_table_name(dataset_id=dataset_id)
        
        try:
            await self.engine.ainit_vectorstore_table(
                table_name=TABLE_NAME,
                vector_size=self.VECTOR_SIZE,
                metadata_columns=[
                    Column("answer", "TEXT"),
                ]
            )
        except ProgrammingError:
            # Catching the exception here
            print("Table already exists. Skipping creation.")

    
    async def delete_vectore_table(self, dataset_id: uuid.UUID) -> None:
        TABLE_NAME = self._get_table_name(dataset_id=dataset_id)
        
        await drop_table(table_name=TABLE_NAME)

    
    
    async def _get_vectorstore_api(self, dataset_id: uuid.UUID) -> PGVectorStore:
        TABLE_NAME = self._get_table_name(dataset_id=dataset_id)
        
        
        vectorstore = await PGVectorStore.create(
            engine=self.engine,
            table_name=TABLE_NAME,
            embedding_service=self.embedding,
        )
        
        return vectorstore
    
    async def _apply_index_reindex(self, dataset_id: uuid.UUID) -> None:
        vectorstore = await self._get_vectorstore_api(dataset_id=dataset_id)
        index = HNSWIndex()
        
        try:
            await vectorstore.aapply_vector_index(index)
        except:
            await vectorstore.areindex()
    
    

    # to remove control characters from content of documents
    # to prevent asyncpg UTF8 0x00 errors.
    def _sanitize_text(self, s: str) -> str:
        if s is None:
            return ""
        if not isinstance(s, str):
            s = str(s)
        # remove null bytes and disallowed control chars except \t, \n, \r
        s = s.replace("\x00", "")
        s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)
        return s

    def _sanitize_documents(self, docs: list[Document]) -> list[Document]:
        for d in docs:
            d.page_content = self._sanitize_text(d.page_content)
            if isinstance(d.metadata, dict):
                for k, v in list(d.metadata.items()):
                    if isinstance(v, str) or v is None:
                        d.metadata[k] = self._sanitize_text(v)
        return docs

    async def add_documents(self, documents: list[Document], dataset_id: uuid.UUID) -> None:
        len_docs = len(documents)
        batch_size = 10
        try:
            await self._init_vector_table(dataset_id=dataset_id)
        finally:
            vectorstore = await self._get_vectorstore_api(dataset_id=dataset_id)
            
            # batched vectorize for handling large number of documents
            for i in range(0, len_docs, batch_size):
                documents_batch = documents[i: i+batch_size]
                documents_batch = self._sanitize_documents(documents_batch)
                _ = await vectorstore.aadd_documents(documents=documents_batch)

            
            await self._apply_index_reindex(dataset_id=dataset_id)
        
        
    async def search(self, query: str, dataset_id: uuid.UUID) -> List[Document]:
        vectorstore = await self._get_vectorstore_api(dataset_id=dataset_id)
        
        
        search_kwrags = {
            'k': self.k_retrieval,
            'score_threshold': self.score_threshold,
        }
        
        retrieved_docs = await vectorstore.asearch(
            query=query,
            search_type=self.search_type,
            **search_kwrags,
        )
        
        return retrieved_docs




vector_db_service = VectorDbService()