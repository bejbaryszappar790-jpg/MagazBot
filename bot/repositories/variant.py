from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums import ChangingData
from bot.errors.server_error import ServerAbsenceError
from bot.models import Variants

"""
Repository for Variants which works with DB.
"""

class VariantRepository:
    def __init__(self, session : AsyncSession):
        self.session = session


    async def create_variant(self,
                            parent_id : int,
                            var_name : str, 
                            var_price : Decimal,
                            quantity : int
                            ):
        new_var = Variants(parent_id = parent_id,
                        var_name = var_name,
                        var_price = var_price,
                        var_quantity = quantity
                        )
        
        self.session.add(new_var)
        await self.session.flush()
    
        return new_var


    async def get_all_variant_names_ids(self, var_name : str, parent_id : int):
        query = (
            select(Variants.var_name,
                Variants.var_id)
            .where(Variants.var_name.ilike(var_name), Variants.parent_id == parent_id)
        )

        result = await self.session.execute(query)

        return result.first()

    

    async def get_variant(self, variant_id : int):
        query = (
            select(
                Variants.var_name,
                Variants.var_price,
                Variants.var_quantity
            )
            .where(Variants.var_id == variant_id)
        )


        result = await self.session.execute(query)

        return result.first()

    async def get_all_variant_names_ids_by_parent_id(self, parent_id : int):
        query = (
            select(
                Variants.var_name,
                Variants.var_id
            )
            .where(Variants.parent_id == parent_id)
        )


        result = await self.session.execute(query)

        rows = result.all()

        answer = {}

        for row in rows:
            answer[row[0]] = row[1]

        return answer

    async def change_variant_data(self, variant_id : int, data : Any, datatype: ChangingData):
        query = (
            select(Variants)
            .where(Variants.var_id == variant_id)
        )

        result = await self.session.execute(query)

        variant = result.scalars().first()

        if variant is None:
            raise ServerAbsenceError("База Данных вернуло None в методе репозиторий варианта change_variant_data.")
        if datatype is ChangingData.VARIANT_NAME:
            variant.var_name = data
        elif datatype is ChangingData.VARIANT_PRICE:
            variant.var_price = data
        elif datatype is ChangingData.VARIANT_QUANTITY:
            variant.var_quantity = data

        return variant
            
        