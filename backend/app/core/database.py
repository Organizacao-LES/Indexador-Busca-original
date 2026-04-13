# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# The standard calling form is to send the URL <database_urls> as the first positional argument, usually a string that indicates database dialect and connection arguments:

#     engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")
print(f"\t\n\n Creating database engine with URL: {settings.DATABASE_URL} \n\n")
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    print(f"New database session created: {db}")
    try:
        print(f"Using database session: {db}")
        yield db
    except Exception as e:
        print(f"Database session error: {e}")
        raise
    finally:
        print(f"Closing database session: {db}")
        db.close()