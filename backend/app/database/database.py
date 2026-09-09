from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import logger

# Create SQLAlchemy engine
# PostgreSQL + PostGIS is primary; SQLite is an explicit fallback for development only when ALLOW_SQLITE_FALLBACK=True
try:
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    engine_kwargs = {
        "pool_pre_ping": True,
        "echo": False
    }
    if db_url.startswith("postgresql"):
        engine_kwargs.update({
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_recycle": settings.DB_POOL_RECYCLE,
        })
    engine = create_engine(
        db_url,
        **engine_kwargs
    )
    # Test connection
    with engine.connect() as conn:
        if db_url.startswith("postgresql"):
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
                logger.info("PostGIS extension verified/enabled.")
            except Exception as pe:
                logger.warning(f"PostGIS extension initialization warning: {pe}")
except Exception as e:
    if settings.ALLOW_SQLITE_FALLBACK:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite engine because ALLOW_SQLITE_FALLBACK=True.")
        engine = create_engine("sqlite:///./disasterguard.db", connect_args={"check_same_thread": False})
    else:
        logger.error(
            f"Failed to connect to primary database at '{settings.DATABASE_URL}': {e}. "
            "Silent SQLite fallback is disabled. Please provide valid PostgreSQL credentials."
        )
        raise RuntimeError(
            f"Database connection failed: {e}. "
            "Please provide valid PostgreSQL credentials in backend/.env (or set ALLOW_SQLITE_FALLBACK=True for dev fallback)."
        ) from e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for acquiring database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
