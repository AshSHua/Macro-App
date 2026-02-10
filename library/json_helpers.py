import json

INDENT = 4

def save_as_json(data:dict, file_path:str):
    '''Function takes an input dict and saves it in an input json file.'''
    if not file_path.endswith(".json"):
        raise ValueError("Input file must be a JSON file.")
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=INDENT)

def retrieve_from_json(file_path:str):
    '''Function takes an input json file path and returns its contents.'''
    if not file_path.endswith(".json"):
        raise ValueError("Input file must be a JSON file.")
    try:
        with open(file_path, 'r') as file:
            data = json.load((file))
            return data
    except json.JSONDecodeError:
        raise ValueError("File does not contain valid JSON")