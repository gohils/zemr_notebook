# import class directly
from zutils1.lib2.sub_dir3 import Module1Class1
# import module directly
from zutils1.lib2.sub_dir3 import module2
# import class directly zutils2\lib22\sub_dir23\module3.py
from zutils2.lib22.sub_dir23 import Module3Class1
# import module directly
from zutils2.lib22.sub_dir23 import module4
if __name__ == "__main__":
    Module1Class1().configure()
    Module1Class1()._run_cmd()
    module2.module2_method1()

    Module3Class1().configure()
    Module3Class1()._run_cmd()
    module4.module4_method1()    