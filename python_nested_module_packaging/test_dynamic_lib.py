# # # import class directly
# from zutils1.lib1.mod3 import Task2Class
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
module_name = "zutils1.lib1.mod1"
task_class_name = 'Task1Class'
input_parameters = {"zkey1":"zvalue1","zkey2":"zvalue2"}
# Load "module.submodule.MyClass"
TaskClass = str_to_class(module_name,task_class_name)
# Instantiate the class (pass arguments to the constructor, if needed)
zcls_inst = TaskClass(input_parameters)
result = zcls_inst.run(input_df)
print(result)

module_name = "zutils1.lib1.mod2"
task_class_name = 'Task2Class'
input_parameters = {"zkey3":"zvalue3"}
# Load "module.submodule.MyClass"
TaskClass = str_to_class(module_name,task_class_name)
# Instantiate the class (pass arguments to the constructor, if needed)
zcls_inst = TaskClass(input_parameters)
result = zcls_inst.run(result)
print(result)

