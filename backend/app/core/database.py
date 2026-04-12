# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# The standard calling form is to send the URL <database_urls> as the first positional argument, usually a string that indicates database dialect and connection arguments:

#     engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
