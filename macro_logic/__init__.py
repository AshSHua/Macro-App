'''
This module contains the base logical classes for this macro. Action represents one single input, ActionManager handles their ordering and execution, essentially acting as an instance of a macro.
'''

from .action import Action
from .action_manager import ActionManager
__all__ = ["Action", "ActionManager"]