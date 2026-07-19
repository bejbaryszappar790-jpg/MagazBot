from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from bot.repositories.product import (
    ProductRepository,
    )
from bot.repositories.user import UserRepository
from bot.errors.common_errors import (
    RoleError,
    DataBaseError,
    PydanticError,
    DuplicateError
)
from bot.schemas.id import Id_In
from bot.models import UserRole
from bot.tools.exist import check_exist


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
                raise RoleError("В сервисе продукта и в методе start_asking_name роль пользователя не подходит админу")
            
            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему то alchemy гонит в сервисе продукта и в методе start_asking_name")
        except ValidationError:
            raise PydanticError("Почему то pydantic не смог изменить тип id в сервисе продуктах.")
        

    async def creating_product(self, parent_name : str) -> bool:
        try:
            product_names_ids = await self.product_repo.get_all_parent_names_ids(parent_name = parent_name)

            if not product_names_ids:
                new_product = await self.product_repo.create_product(parent_name = parent_name)
                if not new_product:
                    raise DataBaseError("Почему то новый продукт не создался")
                
                return True
            
            if check_exist(names = product_names_ids, name = parent_name):
                raise DuplicateError(f"Продукт: {parent_name} уже существует")
                
            new_product = await self.product_repo.create_product(parent_name = parent_name)
            
            if not new_product:
                raise DataBaseError("Почему то новый продукт не создался")
            
            return True
            
        except SQLAlchemyError:
            raise DataBaseError("Почему то база данных не работает в сервисах продукта и в методе создание продукта.")
        