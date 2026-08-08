from bot.repositories.user import UserRepository
from bot.schemas.users.Id_schema import Id_In
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from bot.errors.server_error import (
    DataBaseError,
    ServerPydanticError
    )
from bot.enums import UserRole
from bot.errors.client_error import (
    UnknownUserError,
    RoleError,
)

from bot.enums import UserType
class UserService:

    def __init__(self, user_repo : UserRepository) -> None:
        """
        Конструктор для сервиса пользователей который будет проверять все ошибки и вызывать метода репозиторий.
        В него мы будем кладем обьект репозиторий который будет работать с базами данных даже если не все методы работают с БД.
        """
        self.user_repo = user_repo

    
    async def process_user_start(self, admin_id : int) -> UserType:
        
        try:

            input = Id_In(admin_id = admin_id)
            existing_user = await self.user_repo.search_user(user_id = input.admin_id)

            if existing_user:
                return UserType.EXISTING
            
            new_user = await self.user_repo.register_user(user_id = input.admin_id)
            
            if new_user:
                return UserType.NEW
            
            raise DataBaseError(f"Почему то БД не создал пользователя {admin_id}.")
        except SQLAlchemyError:
            raise DataBaseError(f"Alchemy че то гонит в сервисе пользователя {admin_id} и в методе process_user_start.")
        except ValidationError:
            raise ServerPydanticError(f"Почему то pydantic не смог изменить тип id пользователя {admin_id} сервисе пользователя")



    async def verify_user(self, admin_id : int) -> bool:
            
            try:
                input = Id_In(admin_id = admin_id)
                
                admin_role = await self.user_repo.check_user_role(admin_id = input.admin_id)
    
                if admin_role is None:
                    raise UnknownUserError("У вас нету прав админа что бы создать продукт!", f"Пользователь {admin_id} не зарегестрирован в базе данных но пытается создать продукт.")
                
                
                if admin_role != UserRole.ADMIN:
                    raise RoleError("Вы не являетесь админом что бы создать продукт!", f"Пользователь {admin_id} не является админом но пытается создать продукт!")
    
    
                return True
            except SQLAlchemyError:
                raise DataBaseError("Почему то alchemy гонит в сервисе продукта и в методе start_asking_name")
            except ValidationError:
                raise ServerPydanticError(f"Pydantic почему не смог валидировать {admin_id}.")
        
