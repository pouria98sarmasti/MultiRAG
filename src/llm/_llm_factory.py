"""
LLM Factory for MultiRAG.

This module provides a factory to create appropriate LLM instances
based on the LLM type and other parameters.
"""
import uuid

from src.llm._base_llm import BaseLLM
from src.llm._simple_llm import SimpleLLM
from src.llm._rag_llm import RAGLLM
from src.llm._user_rag_llm import UserRAGLLM
from src.operations._admin import AdminUploadedDatasetInfoOperations
from src.operations._llm import RAGSystemOperations
from src.operations._user import UserUploadedDatasetOperation
from src.schema._llm import LLMType

from src.utils.logger import app_logger

logger = app_logger.getChild("src.llm._llm_factory")


async def create_llm(
    llm_type: LLMType,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    history_limit: int = 5,
    rag_system_id: uuid.UUID | None = None,
) -> BaseLLM:

    if llm_type == LLMType.SIMPLE:
        logger.info(f"Creating Simple LLM for user {user_id}, session {session_id}")
        return SimpleLLM(user_id=user_id, session_id=session_id, history_limit=history_limit)
        
    elif llm_type in (LLMType.RAG, LLMType.USER_RAG):
        # Check if RAG dataset ID is provided
        if rag_system_id:
            rag_system_obj = await RAGSystemOperations().get(rag_system_id=rag_system_id)
            dataset_id = rag_system_obj.dataset_id
        else:
            error_msg = f"RAG system ID is required for LLM type {llm_type.value}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
            
        if llm_type == LLMType.RAG:

            # Get dataset from database
            dataset = await AdminUploadedDatasetInfoOperations().get_by_dataset_id(dataset_id=dataset_id)
            if not dataset:
                error_msg = f"RAG dataset with ID {dataset_id} not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check if the dataset is vectorized
            if not dataset.is_vectorized:
                error_msg = f"RAG dataset with ID {dataset_id} is not vectorized"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Creating RAG LLM for user {user_id}, session {session_id}, dataset {dataset_id}, expertise: {dataset.expertise}")
            return RAGLLM(
                user_id=user_id,
                session_id=session_id,
                dataset_id=dataset_id,
                history_limit=history_limit,
            )
            
        else:  # LLMType.USER_RAG

            # Get dataset from database
            dataset = await UserUploadedDatasetOperation().get_by_dataset_id(dataset_id=dataset_id)
            if not dataset:
                error_msg = f"User dataset with ID {dataset_id} not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check if the dataset is vectorized
            if not dataset.is_vectorized:
                error_msg = f"User dataset with ID {dataset_id} is not vectorized"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Creating User RAG LLM for user {user_id}, session {session_id}, dataset {dataset_id}.")
            return UserRAGLLM(
                user_id=user_id,
                session_id=session_id,
                dataset_id=dataset_id,
            )
    
    else:
        # This should never happen as we're explicitly checking against enum values
        error_msg = f"Unknown LLM type: {llm_type.value}"
        logger.error(error_msg)
        raise ValueError(error_msg) 