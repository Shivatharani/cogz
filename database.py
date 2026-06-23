from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = "sqlite+aiosqlite:///./course.db"


engine = create_async_engine(
    DATABASE_URL,
    echo=True
)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()


async def get_db():

    async with AsyncSessionLocal() as session:

        yield session