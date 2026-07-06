from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bot.models import (
    Parent_Products,
    )



async def create_product(session : AsyncSession, parent_name : str):
    new_product = Parent_Products(parent_name = parent_name)
    session.add(new_product)
    await session.flush()
    return new_product




async def get_all_parent_names_ids(session : AsyncSession, parent_name : str):
    query = (
        select(
            Parent_Products.parent_name,
            Parent_Products.parent_id
            )
        .where(Parent_Products.parent_name.ilike(f"%{parent_name}%"))
    )

    result = await session.execute(query)
    rows = result.all()

    
    answer = {}


    for row in rows:
        answer[row[0]] = row[1]

    
    return answer 




async def search_product_byid(session : AsyncSession, parent_id : int):
    query = (
        select(Parent_Products)
        .where(Parent_Products.parent_id == parent_id)
    )

    result = await session.execute(query)
    return result.scalars().first()



    