from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from bot.errors.client_error import (
    DuplicateError,
)
from bot.errors.server_error import DataBaseError
from bot.repositories.product import (
    ProductRepository,
)
from bot.repositories.user import UserRepository


class ProductService:
    
    def __init__(self, 
                 product_repo : ProductRepository,
                 user_repo : UserRepository
                 ) -> None:
        """
        Class for the service of the product.
        """
        self.product_repo = product_repo
        self.user_repo = user_repo

    async def creating_product(self, parent_name : str, admin_id : int) -> bool:
        try:
            existing_product = await self.product_repo.get_exact_product_by_name(parent_name = parent_name)
            
            if existing_product:
                raise DuplicateError("Такой продукт уже существует!", f"Пользователь {admin_id} пытался создать существующий продукт {parent_name}")
            
            new_product = await self.product_repo.create_product(parent_name = parent_name)
            
            if not new_product:
                raise DataBaseError(f"Продукт который пользователя {admin_id} с именем {parent_name} не был создан.")

            return True

        except IntegrityError:
            raise DuplicateError("Такой продукт уже был создан!", f"Пользователь {admin_id} пытаслся создать продукт {parent_name} который уже был создан!")
        except SQLAlchemyError:
            raise DataBaseError("Почему то база данных не работает в сервисах продукта и в методе создание продукта.")
        