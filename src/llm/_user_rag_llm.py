



import uuid



from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate



from typing_extensions import override


from src.llm._rag_llm import RAGLLM
from src.llm._prompts import UserRAGLLM_Prompt



class UserRAGLLM(RAGLLM):
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
            dataset_id=dataset_id,
            history_limit=history_limit,
        )

    
    @override
    def _get_system_prompt(self) -> SystemMessage:
        return SystemMessage(content=UserRAGLLM_Prompt.system)
    
    @override
    def _get_rag_prompt(self) -> PromptTemplate:
        rag_prompt_template = PromptTemplate.from_template(UserRAGLLM_Prompt.rag)
        
        return rag_prompt_template


