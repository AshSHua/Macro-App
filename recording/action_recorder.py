from macro import Action
from pynput import mouse, keyboard
import threading
import time

class ActionRecorder:
    '''Manages the record feature.'''

    def __init__(self, stop_hotkey:keyboard.Key | keyboard.KeyCode):
        '''
        Docstring for __init__
        
        :param self: self
        :param stop_hotkey: pynput Key or KeyCode that ends the recording session.
        :type stop_hotkey: keyboard.Key | keyboard.KeyCode
        '''

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.recorded_actions = []
        self.stop_hotkey = stop_hotkey
        self.start_time = None #set whenever record is hit



    def record(self):
        '''Starts a recording session that tracks and stores keyboard and mouse inputs until the stop hotkey is pressed.'''
        self.recorded_actions.clear()
        self.start_time = time.perf_counter()

        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)

        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.mouse_listener.join()
        self.keyboard_listener.join()

        self.stop_event.clear()
        return self.recorded_actions

    def _on_click(self, x, y, button, pressed):
        with self.lock:
            if self.stop_event.is_set():
                return False
            location = (x, y)
            if pressed:
                type = "mouse_down"
            else:
                type = "mouse_up"
            timestamp = time.perf_counter() - self.start_time
            action = Action(type=type, input=button, timestamp=timestamp, location=location)
            self.recorded_actions.append(action)
    
    def _on_press(self, key):
        with self.lock:
            timestamp = time.perf_counter() - self.start_time
            action = Action(type="key_down", input=key, timestamp=timestamp, location=None)
            self.recorded_actions.append(action)
    
    def _on_release(self, key):
        with self.lock:
            if key == self.stop_hotkey:
                self.stop_event.set()
                self.mouse_listener.stop()
                self.keyboard_listener.stop()
                return False
            timestamp = time.perf_counter() - self.start_time
            action = Action(type="key_up", input=key, timestamp=timestamp, location=None)
            self.recorded_actions.append(action)