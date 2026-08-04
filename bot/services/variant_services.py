from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from bot.repositories.variant import VariantRepository
from bot.repositories.user import UserRepository
from bot.repositories.product import ProductRepository

from bot.errors.server_error import (
    DataBaseError,
    ServerMissingDataError,
    ServerAbsenceError
)
from bot.errors.client_error import (
    AbsenceError,
    SimpleValidationError,
    DuplicateError,
    BusinessLogicError,
    MissingDataError,
    UnknownUserError
)
from bot.enums import OperationMode
from bot.tools.exist import check_exist
from bot.models import Variants




class VariantService:
    
    def __init__(self, 
                variant_repo : VariantRepository,
                product_repo : ProductRepository,
                user_repo : UserRepository 
                ):
        self.variant_repo = variant_repo
        self.product_repo = product_repo
        self.user_repo = user_repo


    async def get_product_name_for_variant(self, user_id : int, parent_name : str, mode : OperationMode) -> dict:
        try:
            user_type = "Пользователь" if mode is OperationMode.READ else "Админ"

            product_names_ids =  await self.product_repo.get_all_parent_names_ids(parent_name = parent_name)
            
            if not product_names_ids:
                raise AbsenceError("Такого товара не существует!\nНапишите другое имя или же нажмите на кнопку отмена!",
                                   "Словарь с именами и id продуктов пуст в сервисах вариянта и в методе get_ProductNameForVariant"
                                   )
            
            if not check_exist(names = product_names_ids, name = parent_name):
                raise AbsenceError(f"Продукт с именем {parent_name} не существует.", 
                                   f"{user_type} {user_id} пытался создать вариянт для {parent_name} который не существует."
                                                       )
            

            return product_names_ids
        except SQLAlchemyError:
            raise DataBaseError("Почему то БД упало в сервисах вариянта и в методе get_product_name_for_variant")
    
    

    async def get_product_id_for_variant(self, parent_id,
                                      admin_id : int
                                      ) -> bool:
        
        try:
            if admin_id is None:
                raise ServerMissingDataError("Почему то admin_id нету в сервисах вариянта и в методе get_product_id_for_variant")

            existing_product = await self.product_repo.search_product_byid(parent_id)
            if not existing_product:
                raise ServerMissingDataError(f"Пользователь {admin_id} выбрал callback продукт  {parent_id} нету.")
            
            
            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему то БД упало в сервисах вариянта и в методе get_product_id_for_variant")
                



    async def get_variant_name(self, variant_name : str, parent_id : int, admin_id : int) -> bool:
        try:
            
            if not variant_name:
                raise MissingDataError("Вы не написали имя!\nЛибо напиши имя варианта либо нажмите на кнопку отмена!", 
                                    f"Пользователь {admin_id} отправил пустую строку вместо того что бы написать имя варианта!"
                                    )

                
            variant_names_ids = await self.variant_repo.get_all_variant_names_ids(var_name = variant_name, parent_id = parent_id)

            if not variant_names_ids:
                return True
            
            if check_exist(names = variant_names_ids, name = variant_name):
                raise DuplicateError("Такой вариянт существует, напишите другое имя или нажмите на кнопку отмена!", f"Пользователь {admin_id} пытался создать существующий продукт с именем {variant_name} у продукта с id {parent_id}")
            
            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_variant_name")

    
    def get_variant_price(self, input_price : str, admin_id : int):
        try:
            variant_price = Decimal(input_price.replace(",", "."))
            
            if variant_price < 0.0:
                raise BusinessLogicError("Введите цену больше или равно нуля", f"Пользователь пытался написать цену меньше нуля написав {variant_price}")
            
            return variant_price
        except (ValueError, InvalidOperation):
            raise SimpleValidationError("Введите число как: 100, 100.0, 100,0", f"Пользователь {admin_id} написал цену в неприемлимом формате в виде {input_price}")
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_variant_price")
        


    async def finish_creating_variant(self,
                                    quantity : str,
                                    parent_id : int,
                                    var_name : str,
                                    var_price : float,
                                    admin_id : int
             
                               ) -> Variants:
        try:
            if not quantity:
                raise MissingDataError("Вы не написали количество.", f"Пользователь {admin_id} не написал количество.")

            variant_quantity = int(quantity)
            
            if variant_quantity < 0:
                raise BusinessLogicError("Напишите целое число больше или равно нулю.", f"Пользователь {admin_id}")
            
            new_variant = await self.variant_repo.create_variant(
                                                    parent_id = parent_id,
                                                    var_name = var_name,
                                                    var_price = Decimal(str(var_price)),
                                                    quantity = variant_quantity
                                                                )
            if new_variant is None:
                raise ServerMissingDataError("Почему то новый вариянт не создался в сервисах вариянта и в методе finishCreatingVariant.")
            
            return new_variant
        
        except ValueError:
            raise SimpleValidationError("Напишите целое число для количество которое больше или равно нулю.", f"Пользователь {admin_id} написал не правильную количество в виде {quantity}")
        except IntegrityError:
            raise DuplicateError("Такой вариянт уже был создан!", f"Пользователь {admin_id} пытался создать вариянт {var_name} который был создан.")
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе finish_creating_variant")


    async def get_parent_id_for_get_variant(self, parent_name : str, parent_id : int, user_id : int):
        try:
            variant_names_ids = await self.variant_repo.get_all_variant_names_ids_by_parent_id(parent_id = parent_id)

            if not variant_names_ids:
                raise AbsenceError(f"У продукта {parent_name} пока нету вариантов.",
                                   f"Пользователь {user_id} пытался увидеть вариант продукт {parent_name} у которого их нет."
                                    )

            return variant_names_ids
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_parent_id_for_get_variant")
            
    async def get_variant_to_show(self, parent_name : str, 
                                  parent_id : int , 
                                  variant_id : int, 
                                  user_id : int
                                  ):

        try:
            found_variant = await self.variant_repo.get_variant(variant_id = variant_id)

            if not found_variant:
                raise ServerAbsenceError(f"Почему то база данных не нашел вариянт с id {variant_id} продукта {parent_name} с id {parent_id} которого искал пользовалье {user_id}")

            return found_variant
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_variant_to_show")