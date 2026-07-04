from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import (
    Parent_Products,
    Variants,
    Stocks,
    )


async def create_variant(session : AsyncSession, 
                         parent_product : Parent_Products,
                         var_name : str, 
                         var_price : Decimal,
                         quantity : int
                         ):
    new_var = Variants(parent_id = parent_product.parent_id,
                       var_name = var_name,
                       var_price = var_price
                       )
    
    session.add(new_var)
    await session.flush()

    new_stock = Stocks(var_id = new_var.var_id, stock_quantity = quantity)
    session.add(new_stock)
    new_var.stocks.append(new_stock)
    parent_product.variants.append(new_var)

    return new_var