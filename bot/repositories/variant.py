import logging
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models import (
    Parent_Products,
    Variants,
    Stocks,
    )

logger = logging.getLogger(__name__)

"""
Repository for Variants which works with DB.
"""

class VariantRepository:
    def __init__(self, session : AsyncSession):
        self.session = session
        if self.session is None:
            logger.error("Session is None in Product Repo constructor.")
        else:
            logger.info("Product Constructor finished succesfully.")


    async def create_variant(self,
                            parent_product : Parent_Products,
                            var_name : str, 
                            var_price : Decimal,
                            quantity : int
                            ):
        new_var = Variants(parent_id = parent_product.parent_id,
                        var_name = var_name,
                        var_price = var_price
                        )
        
        self.session.add(new_var)
        await self.session.flush()
        new_stock = Stocks(var_id = new_var.var_id, stock_quantity = quantity)

        if new_stock is None and new_var is None:
            logger.error("New variant and New stock is None.")
        elif new_stock is None:
            logger.error("New stock is None.")
        elif new_var is None:
            logger.error("New variant is None.")
        else:
            logger.info("Function finished succesfully.")

        self.session.add(new_stock)
        
        return new_var


    async def get_all_variant_names_ids(self, var_name : str, parent_id : int):
        query = (
            select(Variants.var_name,
                Variants.var_id)
            .where(Variants.var_name.ilike(f"%{var_name}%"), Variants.parent_id == parent_id)
        )

        result = await self.session.execute(query)
        rows = result.all()
        answer = {}

        for row in rows:
            answer[row[0]] = row[1]

        logger.info("Function finished succesfully.")
        return answer