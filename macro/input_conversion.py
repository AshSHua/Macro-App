from pynput import mouse, keyboard

#Helpers to convert pynput Key, KeyCode, and Button objects to strings and vice versa

def key_to_str(key:keyboard.Key | keyboard.KeyCode):
    if isinstance(key, keyboard.KeyCode) and key.char is not None:
        return key.char
    elif isinstance(key, keyboard.Key):
        return f'Key.{key.name}'
    else: 
        return None
    
def str_to_key(s:str):
    if s is None:
        return None
    if s.startswith("Key."):
        name = s.split(".", 1)[1]
        return getattr(keyboard.Key, name)
    else:
        return keyboard.KeyCode.from_char(s)
    
def button_to_str(button:mouse.Button):
    if isinstance(button, mouse.Button):
        return f'Button.{button.name}'
    else:
        return None

def str_to_button(s:str):
    if s is None:
        return None
    if s.startswith("Button"):
        name = s.split(".", 1)[1]
        return getattr(mouse.Button, name)
    else:
        raise ValueError(f'Invalid mouse button string: {s}')