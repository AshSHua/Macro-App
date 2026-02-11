from macro import Action
from pynput import mouse, keyboard
import threading
import time

class ActionRecorder:
    '''Class that tracks user inputs and translates them into Action objects.'''

    def __init__(self):
        self._lock = threading.Lock()
        self.stop_event = threading.Event()
        self._recorded_actions = []
        self._start_time = None #set whenever record is hit

        self._recorder_thread = threading.Thread(target=self._record, daemon=True)

    def _record(self) -> list[Action]:
        '''Starts a recording session that tracks and stores keyboard and mouse inputs until stop is called.'''
        self._recorded_actions.clear()
        
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)

        self._start_time = time.perf_counter()

        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.mouse_listener.join()
        self.keyboard_listener.join()

        self.stop_event.clear()

    def _on_click(self, x, y, button, pressed):
        with self._lock:
            if self.stop_event.is_set():
                return False
            location = (x, y)
            if pressed:
                type = "mouse_down"
            else:
                type = "mouse_up"
            timestamp = time.perf_counter() - self._start_time
            action = Action(type=type, input=button, timestamp=timestamp, location=location)
            self._recorded_actions.append(action)
    
    def _on_press(self, key):
        with self._lock:
            if self.stop_event.is_set():
                return False
            timestamp = time.perf_counter() - self._start_time
            action = Action(type="key_down", input=key, timestamp=timestamp, location=None)
            self._recorded_actions.append(action)
    
    def _on_release(self, key):
        with self._lock:
            if self.stop_event.is_set():
                return False
            timestamp = time.perf_counter() - self._start_time
            action = Action(type="key_up", input=key, timestamp=timestamp, location=None)
            self._recorded_actions.append(action)
            
    def start_record(self):
        '''Wrapper for _record to start it in a different thread so that stop can be safely called.'''
        self.stop_event.clear()
        if self._recorder_thread is not None and self._recorder_thread.is_alive():
            return
        else:
            self._recorder_thread = threading.Thread(target=self._record, daemon=True)
            self._recorder_thread.start()

    def stop_record(self):
        '''Used to stop the recording session. Not applicable to capture.'''
        self.stop_event.set()
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def retrieve_record(self):
        return self._recorded_actions

    def capture(self, mode:str = "both") -> Action:
        '''Starts a (separate) recording session and captures the first event detected. Then, returns it as an Action object. Mode dictates which listeners to activate.'''
        
        action = None

        def on_click(x, y, button, pressed):
            nonlocal action, m_listener, k_listener, start
            if pressed:
                type = "mouse_down"
            else:
                type = "mouse_up"
            location = (x, y)
            now = time.perf_counter()
            action = Action(type=type, input=button, timestamp=(now - start), location=location)
            m_listener.stop()
            k_listener.stop()

        def on_press(key):
            nonlocal action, m_listener, k_listener, start
            now = time.perf_counter()
            action = Action(type="key_down", input=key, timestamp=(now - start), location=None)
            m_listener.stop()
            k_listener.stop()

        def on_release(key):
            nonlocal action, m_listener, k_listener, start
            now = time.perf_counter()
            action = Action(type="key_up", input=key, timestamp=(now - start), location=None)
            m_listener.stop()
            k_listener.stop()

        m_listener = mouse.Listener(on_click=on_click)
        k_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        start = time.perf_counter()

        if mode == "keyboard":
            k_listener.start()
            k_listener.join()
        elif mode == "mouse":
            m_listener.start()
            m_listener.join()
        elif mode == "both":
                m_listener.start()
                k_listener.start()
                m_listener.join()
                k_listener.join()
        else:
            print("wtf")
            return

        return action