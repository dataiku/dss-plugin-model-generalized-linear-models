import ast 

def is_string_list_representation(s):
    try:
        _ = ast.literal_eval(s)
        return isinstance(_, list)
    except:
        return False

def convert_to_list(s):
    try:
        return ast.literal_eval(s)
    except:
        return s  