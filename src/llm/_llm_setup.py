import os

# from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
# import torch

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from src.utils.config import get_config

CHAT_MODEL = get_config('llm.chat.model')
CHAT_TEMPERATURE = get_config('llm.chat.temperature')
CHAT_MAX_TOKENS = get_config('llm.chat.max_tokens')
CHAT_TOP_P = get_config('llm.chat.top_p')
CHAT_BASE_URL = get_config('llm.chat.ollama_url')
CHAT_NUM_CTX = get_config('llm.chat.num_ctx')


EMBEDDING_MODEL = get_config('llm.embedding.model')
OFFLINE = get_config('llm.embedding.offline', True)

# DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


chat_model: BaseChatModel | None = None
embedding_model: Embeddings | None = None


# ensure system will work in fully local environments
def _setup_offline_mode():
    if OFFLINE:
        _ = os.environ.setdefault("HF_HUB_OFFLINE", "1")
        _ = os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        _ = os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def get_chat_model() -> BaseChatModel:
    global chat_model
    if chat_model is None:
        chat_model = ChatOllama(
            model=CHAT_MODEL,
            temperature=CHAT_TEMPERATURE,
            max_tokens=CHAT_MAX_TOKENS,
            top_p=CHAT_TOP_P,
            base_url=CHAT_BASE_URL,
            num_ctx=CHAT_NUM_CTX,
        )
    
    return chat_model

def get_embedding_model() -> Embeddings:
    global embedding_model
    # _setup_offline_mode()
    # if embedding_model is None:
    #     model_kwargs = {'device': DEVICE, 'trust_remote_code': True}
    #     encode_kwargs = {'normalize_embeddings': False}
    #     if OFFLINE:
    #         model_kwargs['local_files_only'] = True
    #     embedding_model = HuggingFaceEmbeddings(
    #         model_name=EMBEDDING_MODEL,
    #         model_kwargs=model_kwargs,
    #         encode_kwargs=encode_kwargs,
    #     )
    
    if embedding_model is None:
        embedding_model = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=CHAT_BASE_URL,
        )
    
    return embedding_model



def setup_llm():
    _ = get_embedding_model().embed_query("Hi")
    _ = get_chat_model().invoke("Hi.")

