from macro import *
from library import *
from recording import *
from gui import *
from platformdirs import user_data_dir
from pathlib import Path

def get_save_directory():
    path = Path(user_data_dir("saves", "MacroApp"))
    path.mkdir(parents=True, exist_ok=True)
    return path
    
path = get_save_directory()

macro = ActionManager()
library = MacroLibrary(path)
recorder = ActionRecorder()

gui = GUI(macro=macro, library=library, recorder=recorder)