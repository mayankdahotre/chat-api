from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.config import get_settings
from app.database.init_db import initialize_databases


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_databases()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Multi-Domain Conversational Analytics Copilot",
        description="Stateful multi-agent DAG backend with Finance and Marketing domain isolation.",
        version="2.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(chat_router, prefix="/api/v1")
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("app.main:app", host=cfg.app_host, port=cfg.app_port, reload=cfg.debug)
