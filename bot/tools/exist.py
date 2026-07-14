

def check_exist(names : dict, name : str,):
    """
    Функция которая проверяет есть ли конкретное имя внутри словаря с именами и id продукта/варияна.
    Возвращает True если есть иначе False.
    """
    for key in names.keys():
        if key.lower() == name.lower():
            return True
        
    
    return False