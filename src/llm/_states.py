


from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_core.documents import Document
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState

from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal



class SimpleLLMStates(MessagesState):
    pass


class RAGLLMStates(MessagesState):
    retrieved_docs: list[Document]
    context: str
    does_use_context: Literal["yes", "no"]
    
    # messages: Annotated[list[AnyMessage], add_messages]



class RelevanceContext(BaseModel):
    binary_score: Literal["yes", "no"]