from bot.repositories.user import UserRepository
from bot.schemas.id import Id_In
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from bot.errors.common_errors import (
    DataBaseError,
    PydanticError
    )
class UserService:

    def __init__(self, user_repo : UserRepository) -> None:
        """
        Конструктор для сервиса пользователей который будет проверять все ошибки и вызывать метода репозиторий.
        В него мы будем кладем обьект репозиторий который будет работать с базами данных даже если не все методы работают с БД.
        """
        self.user_repo = user_repo

    
    async def process_user_start(self, admin_id : int) -> bool:
        
        try:

            input = Id_In(admin_id = admin_id)
            user = await self.user_repo.search_user(user_id = input.admin_id)

            if user:
                return True
            
            new_user = await self.user_repo.register_user(user_id = input.admin_id)
            
            if new_user:
                return False
            
            raise DataBaseError("Почему то БД не создал пользователя.")
        except SQLAlchemyError:
            raise DataBaseError("Alchemy че то гонит в сервисе пользователя и в методе process_user_start.")
        except ValidationError:
            raise PydanticError("Почему то pydantic не смог изменить тип id пользователя сервисе пользователя")
        
