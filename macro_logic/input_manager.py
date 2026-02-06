from pynput import mouse, keyboard

class InputManager:
    '''Wrapper class for pynput keyboard and mouse inputs.'''
    MOUSE = mouse.Controller()
    KEYBOARD = keyboard.Controller()

    @staticmethod
    def move_cursor(x:int, y:int):
        '''Move mouse cursor to exact pixel'''
        InputManager.MOUSE.position = (x, y)

    @staticmethod
    def mouse_down(button:mouse.Button):
        '''Generate a mouse down event'''
        InputManager.MOUSE.press(button=button)
    
    @staticmethod
    def mouse_up(button:mouse.Button):
        '''Generate a mouse up event'''
        InputManager.MOUSE.release(button=button)

    @staticmethod
    def key_down(key:keyboard.Key | keyboard.KeyCode):
        '''Generate a key down event'''
        InputManager.KEYBOARD.press(key=key)

    @staticmethod
    def key_up(key:keyboard.Key | keyboard.KeyCode):
        '''Generate a key up event'''
        InputManager.KEYBOARD.release(key=key)