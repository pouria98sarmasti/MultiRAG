



import uuid

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END


from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# from langchain_text_splitters.character import CharacterTextSplitter



from typing_extensions import override
from collections.abc import AsyncGenerator


from src.llm._base_llm import BaseLLM
from src.llm._prompts import SimpleLLM_Prompt
from src.llm._states import SimpleLLMStates




class SimpleLLM(BaseLLM):
    """
    Simple LLM implementation for general-purpose question answering.
    
    This class extends the BaseLLM with functionality specific to
    the Simple LLM type, including customized system prompts.
    """
    
    
    def __init__(
        self, user_id: uuid.UUID, session_id: uuid.UUID, history_limit: int = 5,
    ) -> None:
        super().__init__(
            user_id=user_id,
            session_id=session_id,
            history_limit=history_limit,
        )
    

    
    
    @override
    def _get_system_prompt(self) -> SystemMessage:
        return SystemMessage(content=SimpleLLM_Prompt.system)
    
    @override
    async def _generation_node(self, state: SimpleLLMStates, config: RunnableConfig):
        
        system_message = self._get_system_prompt()
        # chat_history = state["messages"][-self.history_limit:-1]
        chat_history = state["messages"][:-1]
        human_message = state["messages"][-1]

        if chat_history:
            chat_history = self._custom_trim_messages(chat_history)


        response = await self.chat_model.ainvoke(
            [system_message] + chat_history + [human_message]
        )
        
        return {"messages": response}
        
    
    @override
    def _build_graph(self):
        
        builder = StateGraph(SimpleLLMStates)
        
        builder.add_node("_generation_node", self._generation_node)
        
        builder.add_edge(START, "_generation_node")
        builder.add_edge("_generation_node", END)
        
        graph = builder.compile()
        
        return graph
    
    # async def generate_chat_response(self, user_query: str) -> AsyncGenerator[str, None]:
    #     async for result in super().generate_chat_response(user_query):
    #         yield result