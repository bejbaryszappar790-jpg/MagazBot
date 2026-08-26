from bot.enums import ThingType
from bot.states.add_variant import AddVariantFlow
from bot.states.show_variant import ShowVariantFlow
from bot.states.update_variant import UpdateVariantFlow

previous = "previous"
text = "text"
kb = "kb"
attributes = "attributes"


ADD_VARIANT_NAVIGATION_MAP = {
    AddVariantFlow.waiting_for_parent_id.state : {
        previous : AddVariantFlow.waiting_for_parent_name,
        text : """Вы вернулись в шаг 1!
        Напишите имя продукта чьей вариант вы хотите создать.
        """
    },
    AddVariantFlow.waiting_for_variant_name.state : {
        previous : AddVariantFlow.waiting_for_parent_id,
        kb : ThingType.PRODUCT,
        text : """
            Вы вернулись шагу 2!
            Выберите продукт чьей вариант вы хотите создать.
        """
    },
    AddVariantFlow.waiting_for_price.state : {
        previous : AddVariantFlow.waiting_for_variant_name,
        text : """
            Вы вернулись шагу 3!
            Напишите имя варианта.
        """
    },
    AddVariantFlow.waiting_for_quantity.state : {
        previous : AddVariantFlow.waiting_for_price,
        text : """
        Вы вернулись в шаг 4.
        Напишите цену варианта.
        """
    },
}


SHOW_VARIANT_NAVIGATION_MAP = {
    ShowVariantFlow.waiting_for_parent_id.state : {
        previous : ShowVariantFlow.waiting_for_parent_name,
        text : """
            Вы вернулись шагу 1!
            Напишите имя продукта чьей вариант вы хотите увидеть.
        """
    },
    ShowVariantFlow.waiting_for_variant_id.state : {
        previous : ShowVariantFlow.waiting_for_parent_id,
        kb : ThingType.PRODUCT,
        text : """
            Вы вернулись шагу 2!
            Выберите тот продукт чьей вариант вы хотите увидеть.
        """
    }
}

UPDATE_VARIANT_NAVIGATION_MAP = {
    UpdateVariantFlow.waiting_for_parent_id.state : {
        previous : UpdateVariantFlow.waiting_for_parent_name,
        text : """
            Вы вернулись шагу 1!
            Напишите имя продукта чьей вариант вы хотите изменить!
        """
    },
    UpdateVariantFlow.waiting_for_variant_id.state : {
        previous : UpdateVariantFlow.waiting_for_parent_id,
        kb : ThingType.PRODUCT,
        text : """
            Вы вернулись шагу 2!
            Выберите продукт чьей вариант вы хотите изменить!           
        """
    },
    UpdateVariantFlow.waiting_for_variant_attributes.state : {
        previous : UpdateVariantFlow.waiting_for_variant_id,
        kb : ThingType.VARIANT,
        text : """
            Вы вернулись шагу 3!
            Выберите вариант которую вы хотите изменить!
        """
    },
    UpdateVariantFlow.waiting_for_new_data.state : {
        previous : UpdateVariantFlow.waiting_for_variant_attributes,
        kb : attributes,
        text : """
            Вы вернулись шагу 4!
            Выберите аттрибут варианта которую вы хотите изменить!
        """
    }
}

GLOBAL_BACK_NAVIGATION = { 
    **ADD_VARIANT_NAVIGATION_MAP,
    **SHOW_VARIANT_NAVIGATION_MAP,
    **UPDATE_VARIANT_NAVIGATION_MAP   
}