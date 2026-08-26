from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401
from app.api.routers import auth
from app.api.routers import auth, users
from app.models.statement import Statement  # noqa: F401
from app.api.routers import auth, users, statements
from app.models.transaction import Transaction  # noqa: F401
from app.api.routers import auth, users, statements, analytics
from app.models.subscription import Subscription  # noqa: F401
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinSight AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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