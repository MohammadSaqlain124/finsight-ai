from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app.models.user import User            # noqa: F401
from app.models.statement import Statement  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.core.config import settings
from app.api.routers import auth, users, statements, analytics

app = FastAPI(title="FinSight AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(statements.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSight AI"}