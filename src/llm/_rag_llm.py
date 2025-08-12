


import uuid




from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START, END


from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate



from typing_extensions import override
from collections.abc import AsyncGenerator


from src.operations._vector_db import vector_db_service
from src.llm._base_llm import BaseLLM
from src.llm._prompts import RAGLLM_Prompt
from src.llm._states import RAGLLMStates




class RAGLLM(BaseLLM):
    """
    Simple LLM implementation for general-purpose question answering.
    
    This class extends the BaseLLM with functionality specific to
    the Simple LLM type, including customized system prompts.
    """
    
    
    def __init__(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        dataset_id: uuid.UUID,
        history_limit: int = 5,
    ) -> None:
        super().__init__(
            user_id=user_id,
            session_id=session_id,
            history_limit=history_limit,
        )

        self.dataset_id = dataset_id
        
        self.vector_db = vector_db_service
    


    @override
    def _get_system_prompt(self) -> SystemMessage:
        return SystemMessage(content=RAGLLM_Prompt.system)
    
    def _get_rag_prompt(self) -> PromptTemplate:
        rag_prompt_template = PromptTemplate.from_template(RAGLLM_Prompt.rag)
        
        return rag_prompt_template
    
    
    async def _retrieve_node(self, state: RAGLLMStates, config: RunnableConfig):
        query = state["messages"][-1].content
        retrieved_docs = await self.vector_db.search(
            query=query,
            dataset_id=self.dataset_id,
        )
        
        if retrieved_docs:
            context = "\n".join([doc.page_content + doc.metadata["answer"] for doc in retrieved_docs])
            # chunks = []
            # for i, doc in enumerate(retrieved_docs, 1):
            #     content = doc.page_content + doc.metadata["answer"]
            #     if content:
            #         chunks.append(f"<CHUNK id=\"{i}\">\n{content}\n</CHUNK>")
            # context = "\n\n".join(chunks)
        else:
            context = "Relievent context was not found."
        
        return {"retrieved_docs": retrieved_docs, "context": context}
    

    @override
    async def _generation_node(self, state: RAGLLMStates, config: RunnableConfig):
        
        system_message = self._get_system_prompt()
        chat_history = state["messages"][:-1]
        if chat_history:
            chat_history = self._custom_trim_messages(chat_history)
        
        rag_prompt = self._get_rag_prompt().format(
            user_query=state["messages"][-1].content,
            context=state["context"],
        )
        rag_message = HumanMessage(content=rag_prompt)
        
        response = await self.chat_model.ainvoke(
            [system_message] + chat_history + [rag_message]
        )
        
        return {"messages": response}
        
    
    @override
    def _build_graph(self):
        
        builder = StateGraph(RAGLLMStates)
        
        builder.add_node("_retrieve_node", self._retrieve_node)
        builder.add_node("_generation_node", self._generation_node)
        
        builder.add_edge(START, "_retrieve_node")
        builder.add_edge("_retrieve_node", "_generation_node")
        builder.add_edge("_generation_node", END)
        
        graph = builder.compile()
        
        return graph
    
    # async def generate_chat_response(self, user_query: str) -> AsyncGenerator[str, None]:
    #     async for result in super().generate_chat_response(user_query):
    #         yield result