# # import class directly
# from zutils1.lib2.sub_dir3 import Module1Class1

# # import class directly zutils2\lib22\sub_dir23\module3.py
# from zutils2.lib22.sub_dir23 import Module3Class1

import importlib
def str_to_class(module_name, class_name):
    """Return a class instance from a string reference"""
    try:
        module_ = importlib.import_module(module_name)
        try:
            class_ = getattr(module_, class_name)
        except AttributeError:
            print('Class does not exist')
    except ImportError:
        print('Module does not exist')
    return class_ or None

# Standard import
import importlib
input_df = 'xyz'
module_name = "zutils1.lib2.sub_dir3.module_utils"
task_class_name = 'Task1Class'
input_parameters = {"zkey1":"zvalue1","zkey2":"zvalue2"}
# Load "module.submodule.MyClass"
TaskClass = getattr(importlib.import_module(module_name), task_class_name)
# Instantiate the class (pass arguments to the constructor, if needed)
zcls_inst = TaskClass(input_parameters)
result = zcls_inst.run(input_df)
print(result)

task_class_name = 'Task2Class'
input_parameters = {"zkey3":"zvalue3"}
# Load "module.submodule.MyClass"
TaskClass = str_to_class(module_name,task_class_name)
# Instantiate the class (pass arguments to the constructor, if needed)
zcls_inst = TaskClass(input_parameters)
result = zcls_inst.run(result)
print(result)

# ############ eval
from zutils1.lib2.sub_dir3.module_utils import *
input_df = "df1"
app_input_param = {"zkey4":"zvalue4"}

taks1 = "Task1Class(app_input_param).run(input_df)"
taks2 = "Task2Class(app_input_param).run(input_df)"
taks3 = "Task1Class(app_input_param).run(input_df)"
taks4 = "Task2Class(app_input_param).run(input_df)"

etl_work_flow = [taks1,taks2,taks3,taks4]

print("start of ETL workflow ====> ", input_df)
for task in etl_work_flow:
    input_df :object = eval(task)

print("End of ETL workflow ====> ", input_df)