"""
Database configuration and connection management for microservices.
"""

import os
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration settings"""
    
    def __init__(self):
        # Database connection settings
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "learning_app")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        
        # Connection pool settings
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Build connection URLs
        self.DATABASE_URL = self._build_database_url()
        self.ASYNC_DATABASE_URL = self._build_async_database_url()
    
    def _build_database_url(self) -> str:
        """Build synchronous database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def _build_async_database_url(self) -> str:
        """Build asynchronous database URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class DatabaseManager:
    """Database connection manager with connection pooling"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        
    def get_engine(self):
        """Get or create synchronous database engine"""
        if self._engine is None:
            self._engine = create_engine(
                self.config.DATABASE_URL,
                poolclass=pool.QueuePool,
                pool_size=self.config.POOL_SIZE,
                max_overflow=self.config.MAX_OVERFLOW,
                pool_timeout=self.config.POOL_TIMEOUT,
                pool_recycle=self.config.POOL_RECYCLE,
                pool_pre_ping=True,  # Validate connections before use
                echo=os.getenv("DB_ECHO", "false").lower() == "true"
            )
            logger.info(f"Created database engine with pool_size={self.config.POOL_SIZE}")
        return self._engine
    
    def get_async_engine(self):
        """Get or create asynchronous database engine"""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.config.ASYNC_DATABASE_URL,
                pool_size=self.config.POOL_SIZE,
                max_overflow=self.config.MAX_OVERFLOW,
                pool_timeout=self.config.POOL_TIMEOUT,
                pool_recycle=self.config.POOL_RECYCLE,
                pool_pre_ping=True,
                echo=os.getenv("DB_ECHO", "false").lower() == "true"
            )
            logger.info(f"Created async database engine with pool_size={self.config.POOL_SIZE}")
        return self._async_engine
    
    def get_session_factory(self):
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.get_engine(),
                autocommit=False,
                autoflush=False
            )
        return self._session_factory
    
    def get_async_session_factory(self):
        """Get or create async session factory"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.get_async_engine(),
                class_=AsyncSession,
                autocommit=False,
                autoflush=False
            )
        return self._async_session_factory
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        session = self.get_session_factory()()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with automatic cleanup"""
        session = self.get_async_session_factory()()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database session error: {e}")
            raise
        finally:
            await session.close()
    
    async def close_async_engine(self):
        """Close the async engine and all connections"""
        if self._async_engine:
            await self._async_engine.dispose()
            logger.info("Closed async database engine")
    
    def close_engine(self):
        """Close the sync engine and all connections"""
        if self._engine:
            self._engine.dispose()
            logger.info("Closed database engine")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for dependency injection
def get_db_session() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session"""
    with db_manager.get_session() as session:
        yield session

async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function for FastAPI to get async database session"""
    async with db_manager.get_async_session() as session:
        yield session

# Database initialization functions
def create_tables():
    """Create all database tables"""
    from .models import Base
    engine = db_manager.get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Created all database tables")

async def create_tables_async():
    """Create all database tables asynchronously"""
    from .models import Base
    engine = db_manager.get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Created all database tables (async)")

def drop_tables():
    """Drop all database tables (use with caution!)"""
    from .models import Base
    engine = db_manager.get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("Dropped all database tables")

# Health check function
async def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        async with db_manager.get_async_session() as session:
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Migration support
def get_alembic_config():
    """Get Alembic configuration for migrations"""
    from alembic.config import Config
    from alembic import command
    
    # This would be configured based on your alembic.ini file
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_manager.config.DATABASE_URL)
    return alembic_cfg

def run_migrations():
    """Run database migrations"""
    try:
        from alembic import command
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except ImportError:
        logger.warning("Alembic not installed, skipping migrations")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

# Connection testing
def test_connection():
    """Test database connection"""
    try:
        with db_manager.get_session() as session:
            result = session.execute("SELECT version()")
            version = result.scalar()
            logger.info(f"Database connection successful. PostgreSQL version: {version}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def test_async_connection():
    """Test async database connection"""
    try:
        async with db_manager.get_async_session() as session:
            result = await session.execute("SELECT version()")
            version = result.scalar()
            logger.info(f"Async database connection successful. PostgreSQL version: {version}")
            return True
    except Exception as e:
        logger.error(f"Async database connection failed: {e}")
        return False
