# Python code to illustrate the Modules
import os
import time

class TransformBaseClass:
    def __init__(self, input_dict_params=None):
        self.input_params = input_dict_params
    def run(self, df=None):
        print("zzz Module_utils BaseClass method run is executed")
        print(f"zzz self.input_params is {self.input_params}")
