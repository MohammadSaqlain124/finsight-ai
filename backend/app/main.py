from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401
from app.api.routers import auth
from app.api.routers import auth, users
from app.models.statement import Statement  # noqa: F401
from app.api.routers import auth, users, statements

app = FastAPI(title="FinSight AI")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(statements.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSight AI"}