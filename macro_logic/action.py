from .input_manager import InputManager
from pynput import mouse, keyboard
from .input_conversion import key_to_str, str_to_key, button_to_str, str_to_button
from typing import Self

class Action:
    '''Class representing one base unit for a macro.'''

    def __init__(self, type:str, input:mouse.Button | keyboard.Key | keyboard.KeyCode, timestamp:float, location:tuple[int,int] = None):
        '''
        Docstring for __init__
        
        :param self: self
        :param type: "key_down", "key_up", "mouse_down", or "mouse_up" corresponding to key/mouse down or up.
        :type type: str
        :param input: the pynput object of the key or mouse button to be pressed/released.
        :type input: mouse.Button | keyboard.Key | keyboard.KeyCode
        :param timestamp: time in seconds representing when to activate.
        :type timestamp: float
        :param location: tuple describing which pixel to act on. None to describe current mouse position or non-mouse inputs.
        :type location: tuple[int, int]
        '''
        self.type = type
        self.input = input
        self.timestamp = timestamp
        self.location = location

    def activate(self) -> bool:
        '''Activates the input according to this instance's attributes, then returns True for a down event and False for an up event.'''
        location = self.location
        if location is None:
            location = InputManager.MOUSE.position
        match self.type:
            case "key_down":
                InputManager.key_down(self.input)
                return True
            case "key_up":
                InputManager.key_up(self.input)
                return False
            case "mouse_down":
                InputManager.move_cursor(location[0], location[1])
                InputManager.mouse_down(self.input)
                return True
            case "mouse_up":
                InputManager.move_cursor(location[0], location[1])
                InputManager.mouse_up(self.input)
                return False
            case _:
                raise ValueError("Invalid type.")
            
    def to_dict(self) -> dict:
        '''Returns this instance's data as a dict for serialization.'''
        #convert input to a str
        input = self.input
        if isinstance(input, mouse.Button):
            input = button_to_str(input)
        elif isinstance(input, keyboard.Key) or isinstance(input, keyboard.KeyCode):
            input = key_to_str(input)
        else:
            input = str(input)

        return {
            "type": self.type,
            "input": input,
            "timestamp": self.timestamp,
            "location": self.location
        }
    
    @classmethod
    def from_dict(cls, data:dict) -> Self:
        '''Returns an instance of this class given an input dict.'''
        #convert back to pynput object
        input = data["input"]
        if data["type"] == "mouse_down" or data["type"] == "mouse_up":
            input = str_to_button(input)
        elif data["type"] == "key_down" or data["type"] == "key_up":
            input = str_to_key(input)
        else:
            pass

        return cls(
            type=data["type"],
            input=input,
            timestamp=data["timestamp"],
            location=data["location"]
        )