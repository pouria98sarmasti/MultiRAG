"""
Vector store implementation for embedding storage and retrieval.

This module provides functionality to store and retrieve vector embeddings
using PostgreSQL with pgvector and LangGraph AsyncPostgresStore.
"""

import uuid
from typing import List, Dict, Any, Optional


from src.utils.logger import app_logger
from src.operations._db_setup import get_memory_db

logger = app_logger.getChild("src.operations._memory")


class MemoryService:
    """
    Service for interacting with the vector store.
    
    This class provides methods to store and retrieve vector embeddings
    using LangGraph's AsyncPostgresStore.
    
    Attributes
    ----------
    store : AsyncPostgresStore
        The LangGraph AsyncPostgresStore instance.
    dim : int
        The dimension of the embedding vectors.
    """
    
    def __init__(self) -> None:
        """Initialize the vector store service."""
        self.store = get_memory_db
    
    async def store_memory(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Store a memory in the vector store.
        
        Parameters
        ----------
        user_id : str
            The user ID associated with the memory.
        content : str
            The content of the memory.
        metadata : Dict[str, Any], optional
            Additional metadata for the memory.
            
        Returns
        -------
        uuid.UUID
            The ID of the stored memory in the vector store.
        """
        async with self.store() as store:
            try:
                
                # Prepare metadata
                if metadata is None:
                    metadata = {}
                
                memory_data = {
                    "content": content,
                    "user_id": user_id,
                    "metadata": metadata,
                }
                
                # Create namespace for memory entries
                namespace = ("memories", user_id)
                
                # Generate a unique ID
                memory_id = str(uuid.uuid4())
                
                # Store in vector store
                await store.aput(namespace, memory_id, memory_data)
                
                logger.info(f"Stored memory for user {user_id}, ID: {memory_id}")
                return uuid.UUID(memory_id)
                
            except Exception as e:
                logger.error(f"Error storing memory: {str(e)}")
                raise
    
    async def search_memories(
        self, user_id: str, query: str, limit: int = 5
    ):
        """
        Search for relevant memories using vector similarity.
        
        Parameters
        ----------
        user_id : str
            The user ID to search memories for.
        query : str
            The query string to search.
        limit : int, optional
            Maximum number of results to return.
            
        Returns
        -------
        List[Dict[str, Any]]
            List of memory entries sorted by relevance.
        """
        async with self.store() as store:
            try:
                
                # Create namespace for memory entries
                namespace = ("memories", user_id)
                
                # Search vector store
                results = await store.asearch(
                    namespace,
                    query=query,
                    limit=limit,
                )
                
                logger.info(f"Found {len(results)} relevant memories for user {user_id}")
                return results
                
            except Exception as e:
                logger.error(f"Error searching memories: {str(e)}")
                raise

    async def delete_memory_by_user_id(self, user_id: str):
        
        namespace = ('memories', user_id)
        limit = 100000
        
        async with self.store() as store:
            results = await store.asearch(namespace, limit=limit)
            if results:
                keys = [r.key for r in results]
                for key in keys:
                    await store.adelete(namespace, key=key)
    
    
    
    async def get_memory_by_user_id(self, user_id: str):
        
        namespace = ('memories', user_id)
        limit = 100000
        
        async with self.store() as store:
            results = await store.asearch(namespace, limit=limit)
            if results:
                results = [r.value['content'] for r in results]
                
            return results




# Singleton instance
memory_service = MemoryService()