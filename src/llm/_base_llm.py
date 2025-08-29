"""
Base LLM implementation for MultiRAG.

This module provides the base class for all LLM implementations,
with common functionality for chat, memory, and streaming.
"""

from typing import List, Dict, Any, Optional, AsyncGenerator, Union, Tuple

from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately
)

import uuid
from contextlib import asynccontextmanager
import json

from abc import ABC, abstractmethod

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage, SystemMessage, BaseMessage


from src.utils.logger import app_logger
from src.operations._memory import memory_service
from src.operations._chat_history import chat_history_service
from src.llm._llm_setup import get_chat_model

logger = app_logger.getChild("src.llm._base_llm")


class BaseLLM(ABC):
    """
    Base class for all LLM implementations.
    
    This class provides common functionality for chat, memory, and streaming
    that is used by all LLM types in the MultiRAG system.
    
    Attributes
    ----------
    user_id : str
        The ID of the user.
    session_id : uuid.UUID
        The ID of the chat session.
    chat_history : List[Union[HumanMessage, AIMessage, SystemMessage]]
        The chat history for this session.
    memory_limit : int
        Maximum number of memory entries to retrieve.
    """
    
    def __init__(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        history_limit: int = 5,
        memory_limit: int = 5, 
    ) -> None:
        """
        Initialize the base LLM.
        
        Parameters
        ----------
        user_id : str
            ID of the user.
        session_id : uuid.UUID
            ID of the chat session.
        memory_limit : int, optional
            Maximum number of memory entries to retrieve.
            Default is 5.
        """
        self.user_id = user_id
        self.session_id = session_id
        self.config = {
            "configurable": {
            "thread_id": session_id,
            "user_id": user_id,
            }
        }
        
        self.memory_limit = memory_limit
        self.history_limit = history_limit
        
        self.memory = memory_service
        self.chat_history = chat_history_service
        
        self.chat_model = get_chat_model()
        
        self.compiled_graph = self._build_graph()
        
        logger.info(f"Initialized LLM for user {user_id}, session {session_id}")
    
    
    def _custom_trim_messages(self, messages: list[AnyMessage],
            max_paired_messages_size: int = 100,
            max_total_messages_size: int = 1500):
        trimmed_messages: list[AnyMessage] = []
        len_messages = len(messages)
        step = 2
        for i in range(0, len_messages, step):
            trimmed_message = trim_messages(
                messages[i:i+step],
                strategy="first",
                allow_partial=True,
                token_counter=count_tokens_approximately,
                max_tokens=max_paired_messages_size,
                # start_on="human",
                end_on="ai",
            )
            trimmed_messages.extend(trimmed_message)
        
        trimmed_messages = trim_messages(
            trimmed_messages,
            strategy="last",
            allow_partial=True,
            token_counter=count_tokens_approximately,
            max_tokens=max_total_messages_size,
            start_on="human",
            end_on="ai",
        )
        return trimmed_messages

    @abstractmethod
    def _get_system_prompt(self, mode: str | None = None) -> SystemMessage:
        pass
    
    @abstractmethod
    async def _generation_node(self, state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
        pass
    
    @abstractmethod
    def _build_graph(self):
        pass
    
    async def generate_chat_response(
        self, user_query: str
    ) -> AsyncGenerator[str, None]:
        """
        Generate a chat response to the user query.
        
        Parameters
        ----------
        user_query : str
            The user query.
            
        Yields
        ------
        str
            Chunks of the response as they are generated.
        """
        try:
            
            await self.chat_history.add_user_message(
                message=user_query,
                user_id=self.user_id,
                session_id=self.session_id,
            )
            
            chat_history = await self.chat_history.get_session_messages(
                user_id=self.user_id,
                session_id=self.session_id,
            )
            # chat_history = chat_history[-self.history_limit:]
            
            # Stream the response in json lines format
            counter = 0
            completion = ""
            async for msg, metadata in self.compiled_graph.astream(
                {"messages": chat_history},
                self.config,
                stream_mode="messages",
            ):
                if msg.content and metadata["langgraph_node"]=="_generation_node":
                    counter += 1
                    completion += msg.content
                    result ={
                        "token": msg.content,
                        "index": counter,
                        "completion": completion,
                    }
                    
                    # add \n to create json lines format
                    yield json.dumps(result, ensure_ascii=False) + "\n"
            
            # Add the assistant's message to the chat history
            await self.chat_history.add_ai_message(
                message=completion,
                user_id=self.user_id,
                session_id=self.session_id,
            )
            
        except Exception as e:
            error_msg = f"Error generating chat response: {str(e)}"
            logger.error(error_msg)
            yield f"I'm sorry, there was an error processing your request: {str(e)}" 