from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base_class import Base

# Create a database engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URI
engine = create_engine(str(SQLALCHEMY_DATABASE_URL))

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 