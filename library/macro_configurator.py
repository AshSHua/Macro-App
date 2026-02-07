from macro import *

class MacroConfigurator:
    '''Class to bundle macros with an identifier when saving. Also manages correct conversion between macro-type objects and Python objects.'''

    IDENTIFIER = "VALID_MACRO" #string identifier to check that

    @staticmethod
    def config_macro(macro:ActionManager | list[Action]) -> dict:
        '''Creates and returns a dict containing the serialized macro and the identifier.'''
        if isinstance(macro, ActionManager):
            serialized_macro = macro.to_dict_list()
        elif isinstance(macro, list[dict]):
            serialized_macro = [action.to_dict() for action in macro]
        else:
            raise ValueError("Invalid macro format.")
        return {
            "Identifier": MacroConfigurator.IDENTIFIER,
            "Macro": serialized_macro
        }
    
    @staticmethod
    def validate_macro(data:dict) -> bool:
        '''Checks the input dict for the Identifier key value pair.'''
        if "Identifier" not in data.keys():
            return False
        return data["Identifier"] == MacroConfigurator.IDENTIFIER
    
    @staticmethod
    def strip_macro(data:dict) -> list[Action]:
        '''Basically reverse of config_macro(). Takes the valid macro dict and returns a list of Actions.'''
        if not MacroConfigurator.validate_macro(data=data):
            print("Invalid macro.")
            return
        macro = data["Macro"]
        return [Action.from_dict(action) for action in macro]