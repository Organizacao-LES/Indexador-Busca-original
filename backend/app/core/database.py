# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

print(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    print("Database session created")
    try:
        print("Yielding database session")
        yield db
    except Exception as e:
        print(f"Database session error: {e}")
        raise
    finally:
        print("Closing database session")
        db.close()