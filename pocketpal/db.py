import os

from google.cloud.sql.connector import create_async_connector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

# Database configuration
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

connector = None


async def getconn():
    global connector
    if connector is None:
        connector = await create_async_connector()
    return await connector.connect_async(
        INSTANCE_CONNECTION_NAME, "asyncpg", user=DB_USER, password=DB_PASS, db=DB_NAME
    )


# Create async engine and session factory
engine = create_async_engine(
    "postgresql+asyncpg://",
    async_creator=getconn,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Query execution functions
async def query_with_session(session: AsyncSession, sql: str, **kwargs):
    return await session.execute(text(sql), kwargs)


async def query(sql: str, **kwargs):
    async with AsyncSessionFactory() as session:
        async with session.begin():
            return await query_with_session(session, sql, **kwargs)


async def query_one(sql: str, **kwargs):
    result = await query(sql, **kwargs)
    return result.fetchone()


async def query_scalar(sql: str, **kwargs):
    result = await query(sql, **kwargs)
    return result.scalar()
