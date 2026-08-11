"""Database setup — uses SQLite for local dev, PostgreSQL for production."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        from models import scan, asset, vulnerability, report  # noqa
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables initialized.")


async def get_db():
    """Dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
