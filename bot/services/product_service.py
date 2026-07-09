from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from bot.repositories.product import (
    ProductRepository,
    )
from bot.repositories.user import UserRepository
from bot.errors.common_errors import (
    RoleError,
    DataBaseError,
    PydanticError
)
from bot.schemas.id import Id_In
from bot.models import UserRole



class ProductService:
    
    def __init__(self, product_repo : ProductRepository) -> None:
        "Класс для сервиса продукта."
        self.product_repo = product_repo

    async def start_asking_name(self, admin_id : int, user_repo : UserRepository) -> bool:
        
        try:
            input = Id_In(admin_id = admin_id)
            
            admin_role = await user_repo.check_user_role(admin_id = input.admin_id)

            if admin_role is None:
                raise DataBaseError("Почему то роль пользователя нету в сервисах продукта и в методе start_asking_name")
            
            
            if admin_role != UserRole.ADMIN:
                raise RoleError("В сервисе продукта и в методе start_asking_name роль пользователя не подхит админу")
            
            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему то alchemy гонит в сервисе продукта и в методе start_asking_name")
        except ValidationError:
            raise PydanticError("Почему то pydantic не смог изменить тип id в сервисе продуктах.")