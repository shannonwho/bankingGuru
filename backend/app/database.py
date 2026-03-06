from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    from app.chaos import inject_db_latency, check_db_connection

    # Fault injection hooks — no-ops when chaos is disabled
    try:
        check_db_connection()
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    inject_db_latency()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
