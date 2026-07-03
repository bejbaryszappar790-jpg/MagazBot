from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bot.models import (
    Parent_Products,
    Variants,
    Stocks,
    )


async def create_product(session : AsyncSession, parent_name : str):
    new_product = Parent_Products(parent_name = parent_name)
    session.add(new_product)
    await session.flush()
    return new_product




async def get_all_parent_names_ids(session : AsyncSession, parent_name : str):
    query = (
        select(
            Parent_Products.parent_name,
            Parent_Products.parent_id
            )
        .where(Parent_Products.parent_name.ilike(f"%{parent_name}%"))
    )

    result = await session.execute(query)
    parent_fields = result.all()

    
    answer = {
        "attributes" : {}
    }


    for properties in parent_fields:
        answer["attributes"][properties[0]] = properties[1]

    
    return answer 


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





    