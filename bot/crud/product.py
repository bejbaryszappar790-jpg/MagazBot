from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import Parent_Products

async def create_product(session : AsyncSession, parent_name : str):
    new_product = Parent_Products(parent_name = parent_name)
    session.add(new_product)
    await session.flush()
    return new_product