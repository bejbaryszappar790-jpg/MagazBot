from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from bot.repositories.variant import VariantRepository
from bot.repositories.user import UserRepository
from bot.repositories.product import ProductRepository
from bot.schemas.id import Id_In
from bot.errors.server_error import (
    DataBaseError,
    ServerPydanticError,
)
from bot.errors.client_error import (
    ClientPydanticError,
    RoleError,
    AbsenseError,
    SimpleValidationError,
    DuplicateError,
    BuisnessLogicError,
    MissingDataError,
)
from bot.models import UserRole
from bot.tools.exist import check_exist
from bot.models import Variants


"""
TO DO: 
create server error classes which will be similar to client error classes 
but which are caused by server fault.
"""
class VariantService:
    
    def __init__(self, 
                variant_repo : VariantRepository,
                product_repo : ProductRepository,
                user_repo : UserRepository 
                ):
        self.variant_repo = variant_repo
        self.product_repo = product_repo
        self.user_repo = user_repo


    
    async def start_creating_variant(self, admin_id : int) -> bool:
        
        try:
            input = Id_In(admin_id = admin_id)
            
            admin_role = await self.user_repo.check_user_role(admin_id = input.admin_id)

            if admin_role is None:
                raise DataBaseError("Почему то БД не вернуло роль в сервиса вариянта и в методе start_creating_variant")
            
            if admin_role != UserRole.ADMIN:
                raise RoleError("Вы не админ", f"Пользователь {admin_id} пытается создать вариянт не имея роли админа!")

            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему то Бд упал в сервисах вариянта и в методе start_creating_variant")
        except ValidationError:
            raise ServerPydanticError(f"Почему то pydantic вызвал ошибку при валидаций id {admin_id} хотя это id от телеграмма.")
        


    async def get_ProductNameForVariant(self, parent_name : str) -> dict:
        try:
            product_names_ids =  await self.product_repo.get_all_parent_names_ids(parent_name = parent_name)
            
            if not product_names_ids:
                raise AbsenseError("Словарь с именами и id продуктов пуст в сервисах вариянта и в методе get_ProductNameForVariant", 
                                   "Такого товара не существует!"
                                   )
            
            if not check_exist(names = product_names_ids, name = parent_name):
                raise AbsenseError(f"Продукт с именем {parent_name} не найден среди словарей с похожими продуктами", 
                                   f"Продукт по имени {parent_name} не существует."
                                                       )
            

            return product_names_ids
        except SQLAlchemyError:
            raise DataBaseError("Почему то БД упало в сервисах вариянта и в методе get_ProductNameForVariant")
    
    

    async def get_ProductIdForVariant(self, callback_data : str,
                                      ) -> int:
        text = callback_data.split("_")[1]

        try:
            parent_id = int(text)
            existing_product = await self.product_repo.search_product_byid(parent_id)
            if not existing_product:
                raise AbsenseError(f"Продукт по имени {parent_id} нету.", "Продукт которого вы выбрали не существует.")
            
            
            return parent_id
        except ValueError:
            raise SimpleValidationError(f"{text} не может привсти к типу int.", "")



    async def get_VariantName(self, variant_name : str, parent_id : int) -> bool:
        try:
            variant_names_ids = await self.variant_repo.get_all_variant_names_ids(var_name = variant_name, parent_id = parent_id)

            if not variant_names_ids:
                return True
            
            if check_exist(names = variant_names_ids, name = variant_name):
                raise DuplicateError("Такой вариянт существует!")
            
            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_VariantName")
    
    def get_VariantPrice(self, input_price : str):
        try:
            variant_price = float(input_price.replace(",", "."))
            
            if variant_price < 0.0:
                raise BuisnessLogicError("Введите цену больше или равно нуля")
            
            return variant_price
        except ValueError:
            raise SimpleValidationError("Введите число как: 100, 100.0, 100,0")
        


    async def finishCreatingVariant(self,
                                    quantity : str | None,
                                    parent_id : int | None,
                                    var_name : str | None,
                                    var_price : float | None,
             
                               ) -> Variants:
        try:
            if not quantity:
                raise MisssingDataError("Вы не написали количество.")
            
            variant_quantity = int(quantity)
            
            if variant_quantity < 0:
                raise BuisnessLogicError("Напишите целое число которое больше и равно нулю.")
            
            if parent_id is None:
                raise MisssingDataError("Почему id продукта исчез в сервисах вариянта и методе finishCreatingVariant")
            
            if not var_name:
                raise MisssingDataError("Почему то имя продукта пустой в сервисах вариянта и в методе finishCreatingVariant")
            
            if var_price is None:
                raise MisssingDataError("Почему цена вариянта пустой в сервисах вариянта и методе finishCreatingVariant")
            

            parent_obj = await self.product_repo.search_product_byid(parent_id = parent_id)
            
            if parent_obj is None:
                raise AbsenseError("Почему то мы не нашли продукт по его id в сервисах вариянта и в методе finishCreatingVariant")
            
            new_variant = await self.variant_repo.create_variant(
                                                    parent_product = parent_obj,
                                                    var_name = var_name,
                                                    var_price = Decimal(str(var_price)),
                                                    quantity = variant_quantity
                                                                 )
            
            if new_variant is None:
                raise AbsenseError("Почему то новый вариянт не создался в сервисах вариянта и в методе finishCreatingVariant.")
            
            return new_variant
        except ValueError:
            raise SimpleValidationError("Напишите целое число для количество которое больше или равно нулю.")


