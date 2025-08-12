"""
Database connection and setup utilities.

This module provides functions for setting up database connections
and initializing the database.
"""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from langchain_postgres import PostgresChatMessageHistory
from langchain_postgres import PGEngine
from langchain_postgres.v2.async_vectorstore import AsyncPGVectorStore


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import psycopg


from contextlib import asynccontextmanager

from src.models._base_sqlalchemy import Base
# sqlalchemy lazy loading of mapped classes follow this rule: No Import, No Mappin
from src.models import (_user, _admin, _association_tables, _llm)

from src.utils.config import get_config
from src.utils.logger import setup_logger
from src.llm._llm_setup import get_embedding_model
from src.utils.config import get_config


logger = setup_logger(__name__)

# Build database URI from config
DB_HOST = get_config("database.host")
DB_PORT = get_config("database.port")
DB_NAME = get_config("database.database")
DB_USER = get_config("database.user")
DB_PASSWORD = get_config("database.password")

PSYCOPG_DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_DB_URI = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
PGVECTOR_DB_URI = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
LANGGRAPH_DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable"

# sqlalchemy engine and session
sqlalchemy_engine = create_async_engine(SQLALCHEMY_DB_URI, echo=False)
sqlalchemy_session = async_sessionmaker(bind=sqlalchemy_engine, autocommit=False, autoflush=False, expire_on_commit=False)

# pgvector engine
pg_engine = PGEngine.from_connection_string(url=PGVECTOR_DB_URI)

# embedding model
embedding = get_embedding_model()
VECTOR_SIZE = get_config("llm.embedding.vector_size")

async def setup_langgraph_db():

    async with (
        AsyncPostgresStore.from_conn_string(
            LANGGRAPH_DB_URI,
            index={
                "dims": VECTOR_SIZE,
                "embed": embedding,
                "fields": ["content"],
            },
        ) as store,
        AsyncPostgresSaver.from_conn_string(LANGGRAPH_DB_URI) as checkpointer,
    ):
        await store.setup()
        await checkpointer.setup()


@asynccontextmanager
async def get_memory_db():
    
    async with (
        AsyncPostgresStore.from_conn_string(
            LANGGRAPH_DB_URI,
            index={
                "dims": VECTOR_SIZE,
                "embed": embedding,
                "fields": ["content"],
            },
        ) as store
    ):
        yield store


# sqlalchemy
@asynccontextmanager
async def get_sqlalchemy_db():
    async with sqlalchemy_session() as session:
        yield session

# psycopg
@asynccontextmanager
async def get_psycopg_db():
    async_connection = await psycopg.AsyncConnection.connect(PSYCOPG_DB_URI)
    async with async_connection as conn:
        yield conn

# pgvector
def get_pg_engine():
    return pg_engine

async def drop_table(table_name: str):
    await pg_engine.adrop_table(table_name)



async def setup_sqlalchemy():
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)






