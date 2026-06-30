import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv
from app.models import Users, UserRole


load_dotenv()

admin_str = os.getenv("ADMIN_IDS")


if admin_str is None:
    raise ValueError("Id админов не поддерживается")

admin_ids = list(map(int, admin_str.split(",")))



async def search_user(session : AsyncSession, user_id):
    query = (
        select(Users)
        .where(Users.user_id == user_id)
    )

    result = await session.execute(query)
    
    return result.scalars().first()


async def register_user(session : AsyncSession, user_id : int):
    if user_id in admin_ids:
        new_user = Users(user_id = user_id, user_role = UserRole.ADMIN)
    else:
        new_user = Users(user_id = user_id, user_role = UserRole.USER)

    
    session.add(new_user)
    return new_user