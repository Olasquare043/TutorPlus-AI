from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config import get_settings
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

settings = get_settings()

# Determine if using SQLite or PostgreSQL
if settings.database_url.startswith("sqlite"):
    # SQLite configuration
    logger.info("Using SQLite database")
    
    # Extract database path from URL
    db_path = settings.database_url.replace("sqlite:///", "")
    
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created database directory: {db_dir}")
    
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.debug,
    )
else:
    # PostgreSQL configuration
    logger.info("Using PostgreSQL database")
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.debug,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise