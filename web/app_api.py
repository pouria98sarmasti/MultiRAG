from contextlib import asynccontextmanager

import uvicorn
from src.utils.config import get_config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.operations._db_setup import setup_sqlalchemy, setup_langgraph_db
from src.llm._llm_setup import setup_llm
# from src.models import (_admin, _association_tables, _llm, _user)


from web.routers._admin import admin_router
from web.routers._file import file_router
from web.routers._user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app startup
    setup_llm()
    await setup_langgraph_db()
    await setup_sqlalchemy()

    yield
    # after app shoutdown
    pass



app = FastAPI(lifespan=lifespan, title="Multi RAG")


allow_origins = get_config("app.cors.allow_origins", default=["*"])
allow_credentials = get_config("app.cors.allow_credentials", default=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(file_router, prefix="/file")
app.include_router(user_router, prefix="/user")
app.include_router(admin_router, prefix="/admin")





if __name__ == "__main__":
    host = get_config("app.host", "0.0.0.0")
    port = int(get_config("app.port", 7744))
    reload = bool(get_config("app.debug", True))
    log_level = "debug" if reload else "info"

    # Use string import for reload to work cross-platform
    uvicorn.run("web.app_api:app", host=host, port=port, reload=reload, log_level=log_level)