from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base


engine = create_async_engine("sqlite+aiosqlite:///furniture.db", echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)



async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)