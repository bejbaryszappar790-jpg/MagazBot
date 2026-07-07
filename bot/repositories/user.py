import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models import Users, UserRole




admin_str = os.getenv("ADMIN_IDS")


if admin_str is None:
    raise ValueError("Id админов не поддерживается")

admin_ids = list(map(int, admin_str.split(",")))


class UserRepository:
    
    def __init__(self, session : AsyncSession):
        self.session = session

    async def search_user(self, user_id):
        query = (
            select(Users)
            .where(Users.user_id == user_id)
        )

        result = await self.session.execute(query)
        
        return result.scalars().first()


    async def register_user(self, user_id : int):
        if user_id in admin_ids:
            new_user = Users(user_id = user_id, user_role = UserRole.ADMIN)
        else:
            new_user = Users(user_id = user_id, user_role = UserRole.USER)

        
        self.session.add(new_user)
        await self.session.flush()
        return new_user
    
    async def check_user_role(self, admin_id: int):
        query = (
            select(Users.user_role)
            .where(Users.user_id == admin_id)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()