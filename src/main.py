from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from redis import Redis
from sqlalchemy import text

from src.config import REDIS_URL
from src.database import Base, SessionLocal, engine
from src import models
from src.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    app.state.redis = redis_client
    yield
    redis_client.close()
    engine.dispose()


app = FastAPI(
    title="Docker homework",
    description="API.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/", tags=["System"])
def root():
    return {"name": "TextLab", "swagger": "/docs", "services": ["api", "db", "redis", "worker"]}


@app.get("/health", tags=["System"])
def health(request: Request):
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        request.app.state.redis.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Одна или больше зависимостей не могут быть") from exc
    return {"status": "ok", "postgresql": "ok", "redis": "ok"}
