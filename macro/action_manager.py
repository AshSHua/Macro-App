from .action import Action
import heapq
import itertools
from typing import Self
import time
import threading

class ActionManager:
    '''Class for managing actions: data conversion, ordering, execution.'''

    INTERVAL = 0.001 #interval in seconds denoting how frequently actions are polled for

    def __init__(self, save:list[Action] | None = None):
        '''
        Docstring for __init__
        
        :param self: self
        :param save: list of actions representing execution order for quick initialization.
        :type save: list[Action] | None
        '''
        self.save = list(save) if save is not None else [] #ensures save is a list

        self._counter = itertools.count() #for tie-breaking
        self._execution_order = None #internal heap, type: list[tuple[float, int, Action]]
        self._reset()

        self._downed_actions:set[Action] = set()

        self.running:bool = False #acts like a start or stop flag, start is True, stop is False
        self.looping:bool = False #if True, execution will repeat upon reaching end

    def _reset(self):
        '''Sorts the internal save based on the Actions' timestamps, then sets _execution_order to a copy of save and heapifies it.'''
        self.save.sort(key=lambda a: a.timestamp)
        self._execution_order = [(action.timestamp, next(self._counter), action) for action in self.save]
        heapq.heapify(self._execution_order)

    def add_action(self, action:Action):
        '''Appends an action to self.save then resets to propagate changes.'''
        self.save.append(action)
        self._reset()

    def remove_action(self, action:Action):
        '''Removes an action if it is in self.save, otherwise prints an error message and returns.'''
        if action in self.save:
            self.save.remove(action)
            self._reset()
        else:
            print("Action removal failed: action not found.")

    def _resolve_downed(self):
        '''Generates and executes inverse actions (up events) for each action of type key_down or mouse_down, then clears the set.'''
        inverse_map = {"key_down": "key_up", "mouse_down": "mouse_up"}
        for action in self._downed_actions:
            inverse_type = inverse_map[action.type]
            inverse_action = Action(type=inverse_type, input=action.input, timestamp=None) #timestamp isn't necessary here
            inverse_action.activate()
        self._downed_actions.clear()

    def _run(self):
        '''Starts running macro.'''
        self._reset()
        self.running = True
        start = time.perf_counter()
        if not self._execution_order:
            print("Macro cannot run: is empty")
            return
        next_item = heapq.heappop(self._execution_order) #reminder: _execution_order contains a tuple with the Action object at [2]
        next_time = start + next_item[2].timestamp
        while self.running:
            if time.perf_counter() >= next_time:
                next_action = next_item[2]
                if next_action.activate(): #activate does the action no matter what and returns boolean
                    self._downed_actions.add(next_action)
                else:
                    self._downed_actions.discard(next_action)
                if not self._execution_order:
                    if self.looping:
                        self._reset()
                        start = time.perf_counter()
                    else:
                        break
                next_item = heapq.heappop(self._execution_order)
                next_time = start + next_item[2].timestamp
            time.sleep(ActionManager.INTERVAL)
        self._resolve_downed()
        self.running = False
        self._reset()

    def start(self):
        '''Essentially a wrapper for self._run() in a daemon thread to prevent blocking.'''
        macro_thread = threading.Thread(target=self._run, daemon=True)
        macro_thread.start()

    def stop(self):
        '''Stops execution.'''
        self.running = False

    def to_dict_list(self) -> list[dict]:
        '''Converts self.save into a list of dicts for serialization.'''
        return [action.to_dict() for action in self.save]

    @classmethod
    def from_dict_list(cls, data:list[dict]) -> Self:
        '''Returns an instance of this class given an input list of dicts.'''
        action_list = [Action.from_dict(action) for action in data]
        return cls(save=action_list)