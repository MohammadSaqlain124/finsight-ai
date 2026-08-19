from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For now this is hardcoded. In Step 3, when we add secret keys for login,
# we'll move this into a proper config/.env file. One thing at a time.
DATABASE_URL = "sqlite:///./finsight.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-specific; needed for FastAPI
)

# A factory that produces new Session objects when we need them.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Hands a fresh database session to whoever needs it, then guarantees
    it gets closed afterward — even if an error happens. FastAPI calls this
    automatically for each request in later steps."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()