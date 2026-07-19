from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models import (
    Parent_Products,
    )


class ProductRepository:

    def __init__(self, session : AsyncSession):
        self.session = session


    async def create_product(self, parent_name : str):
        new_product = Parent_Products(parent_name = parent_name)
        self.session.add(new_product)
        await self.session.flush()
        return new_product




    async def get_all_parent_names_ids(self, parent_name : str):
        query = (
            select(
                Parent_Products.parent_name,
                Parent_Products.parent_id
                )
            .where(Parent_Products.parent_name.ilike(f"%{parent_name}%"))
        )

        result = await self.session.execute(query)
        rows = result.all()

        
        answer = {}


        for row in rows:
            answer[row[0]] = row[1]

        
        return answer 




    async def search_product_byid(self, parent_id : int):
        query = (
            select(Parent_Products)
            .where(Parent_Products.parent_id == parent_id)
        )

        result = await self.session.execute(query)
        return result.scalars().first()



        