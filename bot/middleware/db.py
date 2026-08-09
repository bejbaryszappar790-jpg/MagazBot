from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.repositories.product import ProductRepository
from bot.repositories.user import UserRepository
from bot.repositories.variant import VariantRepository
from bot.services.product_services import ProductService
from bot.services.user_services import UserService
from bot.services.variant_services import VariantService


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool : async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self,
                       handler : Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event : TelegramObject,
                       data : Dict[str, Any]
                       ) -> Any:
            async with self.session_pool() as session:
                data["session"] = session
                user_repo = UserRepository(session = session)
                product_repo = ProductRepository(session = session)
                variant_repo = VariantRepository(session = session)
                
                
                
                data["user_service"] = UserService(user_repo = user_repo)
                
                data["product_service"] = ProductService(product_repo = product_repo,
                                                         user_repo = user_repo
                                                         )
                
                data["variant_service"] = VariantService(variant_repo = variant_repo,
                                                         product_repo = product_repo,
                                                         user_repo = user_repo
                                                         )
                
                try:
                    result = await handler(event, data)
                    await session.commit()
                    return result
                except Exception:
                    await session.rollback()
                    raise