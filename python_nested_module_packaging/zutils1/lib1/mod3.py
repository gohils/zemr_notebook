import os
import time

from zutils1.lib1.mod_base import BaseClass

class Task3Class(BaseClass):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)

    def run(self, df=None):
        print("zzz mod3 Task3Class method run is executed")
        print(f"zzz self.input_params is {self.input_params}")
        result = str(df) + '------' + __class__.__name__
        return result