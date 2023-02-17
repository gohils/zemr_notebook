import os
import time

class BaseClass:
    def __init__(self, input_dict_params=None):
        self.input_params = input_dict_params
    def run(self, df=None):
        print("zzz Module_utils BaseClass method run is executed")
        print(f"zzz self.input_params is {self.input_params}")

class Task1Class(BaseClass):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)

    def run(self, df=None):
        print("zzz Module_utils Task1Class method run is executed")
        print(f"zzz self.input_params is {self.input_params}")
        result = str(df) + '------' + __class__.__name__
        return result

class Task2Class(BaseClass):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)

    def run(self, df=None):
        print("zzz Module_utils Task2Class method run is executed")
        print(f"zzz self.input_params is {self.input_params}")
        result = str(df) + '------' + __class__.__name__
        return result

