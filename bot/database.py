import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()
DB_URL = os.getenv("ALCHEMY_DATABASE_URL")


if DB_URL is None:
    raise ValueError("Database url is empty")


Base = declarative_base()
engine = create_async_engine(DB_URL)
SessionLocal = async_sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)
