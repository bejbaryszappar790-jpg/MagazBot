from bot.states.add_product import AddProductFlow
from bot.states.add_variant import AddVariantFlow

BACK_NAVIGATION_MAP = {
    AddProductFlow.waiting_for_name.state: {
        "previous" : None,
        "text" : "Действие отменено\nВыберите команду."
    }
    
}

VARIANT_NAVIGATION_MAP = {
    AddVariantFlow.waiting_for_parent_name.state : {
            "previous" : None,
            "text" : "Действие отменено\nВыберите команду."
        },
    AddVariantFlow.waiting_for_parent_id.state : {
        "previous" : AddVariantFlow.waiting_for_parent_name,
        "text" : """Вы вернулись в шаг 1!
        Напишите имя продукта чьей вариант вы хотите создать.
        """
        },
    AddVariantFlow.waiting_for_variant_name.state : {
        "previous" : AddVariantFlow.waiting_for_parent_id,
        "text" : """
            Вы вернулись шагу 2!
            Выберите имя 
        """
    }
}