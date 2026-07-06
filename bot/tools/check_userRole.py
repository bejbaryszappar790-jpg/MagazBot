from sqlalchemy.ext.asyncio import AsyncSession
from bot.repositories.user import search_user

async def check_user_role(session : AsyncSession, user_id : int):

    
    user = await search_user(session = session, user_id = user_id)
    
    if user is None:
        return None
    
    
    return user.user_role