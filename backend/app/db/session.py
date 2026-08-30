from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

database_url = settings.DATABASE_URL

# Some hosts hand out the older "postgres://" scheme, which SQLAlchemy rejects.
# Normalize it to "postgresql://".
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# check_same_thread is SQLite only, so only pass it for SQLite.
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Hands out a fresh database session and closes it afterward, even if an
    error happens."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()