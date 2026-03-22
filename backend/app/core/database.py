# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# The standard calling form is to send the URL <database_urls> as the first positional argument, usually a string that indicates database dialect and connection arguments:

#     engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

engine = create_engine(
    f"postgresql+psycopg2://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/ifesdoc"
)

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
