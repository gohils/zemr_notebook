# import class directly
# from zutils1.lib1 import *
# # import module directly
# from zutils1.lib2 import module2
from zcombined.composites.lib3 import *

print("test")
input_parameters = {"zkey1":"zvalue1","zkey2":"zvalue2"}
zcls_inst = Trans1Class(input_parameters)
result = zcls_inst.run('input_df')

zcls_inst = Trans2Class(input_parameters)
zcls_inst.run(result)