"""
Database connection manager for the Horse Race Handicapping AI system.
Manages SQLAlchemy database connections and sessions.
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from src.core.logging import get_logger
from src.models.database import Base

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database connection manager for handling database operations.
    Supports both synchronous and asynchronous database connections.
    """
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self._database_url: Optional[str] = None
    
    async def connect(self, database_url: str, echo: bool = False) -> None:
        """
        Initialize database connections.
        
        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements
        """
        self._database_url = database_url
        
        # Create synchronous engine
        self.engine = create_engine(
            database_url.replace("postgresql://", "postgresql://"),
            echo=echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        # Create asynchronous engine
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.async_engine = create_async_engine(
            async_url,
            echo=echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        # Create session factories
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Database connections initialized", database_url=database_url)
    
    async def disconnect(self) -> None:
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        
        if self.engine:
            self.engine.dispose()
        
        logger.info("Database connections closed")
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        if not self.async_engine:
            raise RuntimeError("Database not connected")
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        if not self.async_engine:
            raise RuntimeError("Database not connected")
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped")
    
    def get_session(self) -> Session:
        """
        Get a synchronous database session.
        
        Returns:
            Database session
        """
        if not self.session_factory:
            raise RuntimeError("Database not connected")
        
        return self.session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an asynchronous database session context manager.
        
        Yields:
            Async database session
        """
        if not self.async_session_factory:
            raise RuntimeError("Database not connected")
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_async_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency for getting async database sessions.
        
        Yields:
            Async database session
        """
        async with self.get_async_session() as session:
            yield session


# Global database manager instance
database_manager = DatabaseManager()


# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async for session in database_manager.get_async_session_dependency():
        yield session
