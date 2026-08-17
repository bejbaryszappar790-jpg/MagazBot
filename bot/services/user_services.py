from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from bot.enums import ThingType, UserRole, UserType
from bot.errors.client_error import (
    RoleError,
    UnknownUserError,
)
from bot.errors.server_error import DataBaseError, ServerPydanticError
from bot.repositories.user import UserRepository
from bot.schemas.users.Id_schema import Id_In


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



    async def verify_user(self, admin_id : int, thing_type : ThingType) -> bool:
            
            try:
                
                admin_role = await self.user_repo.check_user_role(admin_id = admin_id)

                thing = "продукт" if thing_type == ThingType.PRODUCT else "вариант"
                if admin_role is None:
                    raise UnknownUserError(f"У вас нету прав админа что бы создать {thing}!", 
                                           f"Пользователь {admin_id} не зарегестрирован в базе данных но пытается создать {thing}.", 
                                           clear_state = True
                                           )
                
                
                if admin_role != UserRole.ADMIN:
                    raise RoleError(f"Вы не являетесь админом что бы взаимодействовать {thing}!", 
                                    f"Пользователь {admin_id} не является админом но пытается взаимодействовать {thing}!", 
                                    clear_state = True
                                    )
    
    
                return True
            except SQLAlchemyError:
                raise DataBaseError("Почему то alchemy гонит в сервисе продукта и в методе start_asking_name")
            except ValidationError:
                raise ServerPydanticError(f"Pydantic почему не смог валидировать {admin_id}.")
        
