from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import search_user, register_user
from app.schemas.sessionstart import SessionStart_In, SessionStart_Out
router = Router()


@router.message(CommandStart())
async def start_session(message : Message, session : AsyncSession):
    user_id  = message.from_user.id

    input = SessionStart_In(user_id = user_id)

    existing_user = await search_user(session = session, user_id = input.user_id)

    if existing_user:
        return existing_user

    
    new_user = await register_user(session = session, user_id = input.user_id)
    
    return new_user
