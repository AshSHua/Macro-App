from macro import *
from library import *
from recording import *
from gui import *
from pynput import keyboard
import time

macro = ActionManager()
library = MacroLibrary(r'C:\Users\asher\OneDrive\Documents\GitHub\Macro-App\saves')
recorder = ActionRecorder()

gui = GUI(macro=macro, library=library, recorder=recorder)