# import class directly
from zutils2.lib2 import *
# # import module directly
# from zutils1.lib2 import module2

print("test")
input_parameters = {"zkey1":"zvalue1","zkey2":"zvalue2"}
zcls_inst = Transform1Class(input_parameters)
zcls_inst.run('xyz')

