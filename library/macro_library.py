import os
from .macro_configurator import MacroConfigurator
from library.json_helpers import save_as_json, retrieve_from_json 
from macro import *

class MacroLibrary:
    '''Class for macro storage and management.'''
    
    ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-") #set of valid chars for file names
    MAX_NAME_LENGTH = 16 #maximum length for file names

    def __init__(self, folder_path:str):
        '''
        Docstring for __init__
        
        :param self: self
        :param folder_path: Path to folder which acts as the macro save folder.
        :type folder_path: str
        '''

        self.save_folder = folder_path #save folder
        
        self.index = {} #dict mapping macro file names to their path
        self._fix_index()
    
    @staticmethod
    def _validate_file(file_path:str) -> bool:
        '''Wrapper for retrieve_from_json() and MacroConfig.validate_macro(). Checks file for valid JSON and a valid macro.'''
        try:
            data = retrieve_from_json(file_path=file_path)
        except ValueError: #retreive_from_json throws ValueErrors
            return False
        return MacroConfigurator.validate_macro(data=data)

    @staticmethod
    def _validate_name(name:str):
        '''Checks input name string against the class constants, raising a ValueError if name is invalid.'''
        if (not all(char in MacroLibrary.ALLOWED_CHARS for char in name)):
            raise ValueError("Invalid name: invalid character.")
        if (len(name) > MacroLibrary.MAX_NAME_LENGTH):
            raise ValueError("Invalid name: name too long.")

    def _fix_index(self):
        '''Scans the save folder and populates index with valid macro json files.'''
        for file in os.listdir(self.save_folder):
            file_path = os.path.join(self.save_folder, file)
            if MacroLibrary._validate_file(file_path):
                name = file[:-5]
                self.index[name] = file_path

    def index_collision(self, name:str) -> bool:
        '''Checks if name is a key in index. If so, return True, else return False.'''
        return name in self.index
    
    def save_macro(self, macro:ActionManager | list[Action], name:str, overwrite:bool = False):
        '''Saves a macro. If overwrite is True, then the existing save with the same name is overwritten.'''
        serialized_macro = MacroConfigurator.config_macro(macro)
        file_path = os.path.join(self.save_folder, f'{name}.json')
        if self.index_collision(name):
            if overwrite:
                pass
            else:
                return
        save_as_json(serialized_macro, file_path)
        self.index[name] = file_path

    def retrieve_macro(self, name:str) -> list[Action]:
        '''Retrieves a macro. Raises FileNotFoundError if the macro save doesn't exist.'''
        if not self.index_collision(name):
            raise FileNotFoundError()
        data = retrieve_from_json(self.index[name])
        macro = MacroConfigurator.strip_macro(data)
        return macro
    
    def delete_macro(self, name:str):
        '''Deletes a macro. Raises FileNotFoundError if the macro save doesn't exist.'''
        if not self.index_collision(name):
            raise FileNotFoundError()
        os.remove(self.index[name])
        self.index.pop(name)