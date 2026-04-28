import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import redis
from backend_v2.core.config import settings

logger = logging.getLogger("database_manager")

# PostgreSQL Configuration
# Using the URL provided by user
DATABASE_URL = "postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database schema."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db():
    """Dependency for FastAPI to provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
