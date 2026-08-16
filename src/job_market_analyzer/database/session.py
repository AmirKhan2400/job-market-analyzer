from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from job_market_analyzer.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
)

SessionLocal = sessionmaker(
    bind=engine,
)
