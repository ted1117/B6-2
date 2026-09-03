from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.todos import router as todos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(todos_router)
