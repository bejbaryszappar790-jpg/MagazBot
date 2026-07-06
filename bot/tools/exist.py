

def check_exist(names : dict, name : str,):

    for key in names.keys():
        if key.lower() == name.lower():
            return "exist"
        
    
    return "not exist"