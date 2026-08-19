from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401  (see note below)

app = FastAPI(title="FinSight AI")

# DEV ONLY: build any missing tables from our models at startup.
# In production we'll replace this with Alembic migrations (a later phase).
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSight AI"}