from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # PostgreSQL specific configuration
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True,
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# For direct session creation (backwards compatibility)
SessionLocal = lambda: Session(engine)