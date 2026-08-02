from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from bot.repositories.variant import VariantRepository
from bot.repositories.user import UserRepository
from bot.repositories.product import ProductRepository
from bot.schemas.id import Id_In
from bot.errors.server_error import (
    DataBaseError,
    ServerPydanticError,
    ServerAbsenceError,
    ServerValidationError,
    RecheckError,
    ServerMissingDataError
)
from bot.errors.client_error import (
    RoleError,
    AbsenceError,
    SimpleValidationError,
    DuplicateError,
    BusinessLogicError,
    MissingDataError,
    UnknownUserError
)
from bot.enums import UserRole
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


    
    async def start_creating_variant(self, admin_id : int) -> bool:
        
        try:
            input = Id_In(admin_id = admin_id)
            
            admin_role = await self.user_repo.check_user_role(admin_id = input.admin_id)

            if admin_role is None:
                raise UnknownUserError("У вас нету прав админа что бы создать вариянт!", f"Пользователь {admin_id} не зарегестрирован в базе данных но пытается создать вариянт.")
            
            if admin_role != UserRole.ADMIN:
                raise RoleError("Вы не админ", f"Пользователь {admin_id} пытается создать вариянт не имея роли админа!")

            return True
        except SQLAlchemyError:
            raise DataBaseError("Почему то Бд упал в сервисах вариянта и в методе start_creating_variant")
        except ValidationError:
            raise ServerPydanticError(f"Почему то pydantic вызвал ошибку при валидаций id {admin_id} хотя это id от телеграмма.")
        


    async def get_product_name_for_variant(self, admin_id : int, parent_name : str) -> dict:
        try:
            if not parent_name:
                MissingDataError("Вы не написали имя!\nЛибо напиши имя продукта либо нажмите на кнопку отмена!", 
                                 f"Пользователь {admin_id} отправил пустую строку вместо того что бы написать имя продукта!"
                                 )
            product_names_ids =  await self.product_repo.get_all_parent_names_ids(parent_name = parent_name)
            
            if not product_names_ids:
                raise AbsenceError("Такого товара не существует!\nНапишите другое имя или же нажмите на кнопку отмена!",
                                   "Словарь с именами и id продуктов пуст в сервисах вариянта и в методе get_ProductNameForVariant"
                                   )
            
            if not check_exist(names = product_names_ids, name = parent_name):
                raise AbsenceError(f"Продукт с именем {parent_name} не существует.", 
                                   f"Пользователь {admin_id} пытался создать вариянт для {parent_name} который не существует."
                                                       )
            

            return product_names_ids
        except SQLAlchemyError:
            raise DataBaseError("Почему то БД упало в сервисах вариянта и в методе get_product_name_for_variant")
    
    

    async def get_product_id_for_variant(self, text : str,
                                      admin_id : int
                                      ) -> int:
        
        try:
            if admin_id is None:
                raise ServerMissingDataError("Почему то admin_id нету в сервисах вариянта и в методе get_product_id_for_variant")

            if not text:
                raise ServerMissingDataError("Почему то текст parent_id нету в сервисах вариянта и в методе get_product_id_for_variant")
            
            parent_id = int(text)
            existing_product = await self.product_repo.search_product_byid(parent_id)
            if not existing_product:
                raise ServerMissingDataError(f"Пользователь {admin_id} выбрал callback продукт  {parent_id} нету.")
            
            
            return parent_id
        except ValueError:
            raise ServerValidationError(f"{text} от пользвоателя {admin_id} не может быть приведен к типу int.")
        except SQLAlchemyError:
            raise DataBaseError("Почему то БД упало в сервисах вариянта и в методе get_product_id_for_variant")
                



    async def get_variant_name(self, variant_name : str, parent_id : int, admin_id : int) -> bool:
        try:
            
            if not variant_name:
                MissingDataError("Вы не написали имя!\nЛибо напиши имя варианта либо нажмите на кнопку отмена!", 
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
                                    quantity : str | None,
                                    parent_id : int | None,
                                    var_name : str | None,
                                    var_price : float | None,
                                    admin_id : int
             
                               ) -> Variants:
        try:
            if not quantity:
                raise MissingDataError("Вы не написали количество.", f"Пользователь {admin_id} не написал количество.")
            
            variant_quantity = int(quantity)
            
            if variant_quantity < 0:
                raise BusinessLogicError("Напишите целое число больше или равно нулю.", f"Пользователь {admin_id}")
            
            if parent_id is None:
                raise RecheckError(f"{parent_id} от {admin_id} которую мы получили до этого был правилен а теперь нет.")
            
            if not var_name:
                raise RecheckError(f"{var_name} от {admin_id} которую мы получили до этого был правилен а теперь нет.")
            
            if var_price is None:
                raise RecheckError(f"{var_price} от {admin_id} которую мы получили до этого был правилен а теперь нет.")
            

            parent_obj = await self.product_repo.search_product_byid(parent_id = parent_id)
            
            if parent_obj is None:
                raise RecheckError(f"Продукт {parent_id} который был выбран {admin_id} до этого существовал а теперь его нету.")
            
            new_variant = await self.variant_repo.create_variant(
                                                    parent_product = parent_obj,
                                                    var_name = var_name,
                                                    var_price = Decimal(str(var_price)),
                                                    quantity = variant_quantity
                                                                 )
            
            if new_variant is None:
                raise ServerMissingDataError("Почему то новый вариянт не создался в сервисах вариянта и в методе finishCreatingVariant.")
            
            return new_variant
        
        except (ValueError, InvalidOperation):
            raise SimpleValidationError("Напишите целое число для количество которое больше или равно нулю.", f"Пользователь {admin_id} написал не правильную количество в виде {quantity}")
        except IntegrityError:
            raise DuplicateError("Такой вариянт уже был создан!", f"Пользователь {admin_id} пытался создать вариянт {var_name} который был создан.")
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе finish_creating_variant")


    async def get_parent_name_for_get_variant(self, parent_name : str | None, user_id : int):
        try:
            if user_id is None:
                raise ServerMissingDataError("Нету admind_id в сервисах варианта в методе get_parent_name_for_get_variant.")

            if not parent_name:
                raise MissingDataError("Вы не написали имя!\nЛибо напиши имя продукта либо нажмите на кнопку отмена!", 
                                    f"Пользователь {user_id} отправил пустую строку вместо того что бы написать имя продукта!"
                                    )    

            product_names_ids = await self.product_repo.get_all_parent_names_ids(parent_name = parent_name)

            if not product_names_ids:
                raise AbsenceError("Такого продукта не существует!\nНапишите другой продкут или же нажмите на кнопку отмена!", 
                             f"Пользователь {user_id} пытался увидеть продукт {parent_name} который не существует."
                             )


            if not check_exist(names = product_names_ids, name = parent_name):
                raise AbsenceError("Такого продукта не сущетсвует!\nНапишите другой продукт или же нажмите на кнопку отмена",
                             f"Пользователь {user_id} пытался увидеть продукт {parent_name} который не существует."
                             )

            return product_names_ids
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_parent_name_for_get_variant")


    async def get_parent_id_for_get_variant(self, parent_name : str | None, text : str, user_id : int):
        try:
            if not parent_name:
                raise RecheckError(f"parent_name от пользователя {user_id} пуст хотя до этого мы проверяли он не был таким.")
            parent_id = int(text)
            
            variant_names_ids = await self.variant_repo.get_all_variant_names_ids_by_parent_id(parent_id = parent_id)

            if not variant_names_ids:
                raise AbsenceError(f"У продукта {parent_name} пока нету вариантов.",
                                   f"Пользователь {user_id} пытался увидеть вариант продукт {parent_name} у которого их нет."
                                    )

            return variant_names_ids
        except ValueError:
            raise ServerValidationError(f"Мы не смогли привести тип {text} в int.")
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_parent_id_for_get_variant")
            
    async def get_variant_to_show(self, parent_name : str | None, 
                                  parent_id : int | None, 
                                  text : str, 
                                  user_id : int | None
                                  ):

        try:
            variant_id = int(text)
            if variant_id is None:
                ServerMissingDataError(f"id варията который выбрал пользователь {user_id} пуст.")

            if user_id is None:
                raise RecheckError(f"Почему то id пользователя который выбирал ранее продукт {parent_id} и писал {parent_name} пуст.")   
            if parent_id is None:
                raise RecheckError(f" {parent_id} продукта {parent_id} от пользователя {user_id} стал пустым почему то.")

            
            if not parent_name:
                raise RecheckError(f"Продукт {parent_name} c {parent_id} от пользователя {user_id} стал пустым почему то.")

            found_variant = await self.variant_repo.get_variant(variant_id = variant_id)

            if not found_variant:
                raise ServerAbsenceError(f"Почему то база данных не нашел вариянт с id {variant_id} продукта {parent_name} с id {parent_id} которого искал пользовалье {user_id}")

            return found_variant
        except ValueError:
            raise ServerValidationError(f"Произошла ошибка когда сервер пытался привести тип id варианта {text} к int.")
        except SQLAlchemyError:
            raise DataBaseError("Почему БД упал в сервисе вариянта и в методе get_variant_to_show")
        



        