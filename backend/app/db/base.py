from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Every ORM model inherits from this.
    SQLAlchemy uses Base to keep a registry of all tables (its 'metadata'),
    which is how it knows what to create in the database."""
    pass