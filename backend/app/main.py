from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401
from app.api.routers import auth

app = FastAPI(title="FinSight AI")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSight AI"}