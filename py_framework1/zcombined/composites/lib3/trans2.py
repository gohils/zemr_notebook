from zutils1.lib1.mod2 import Task2Class
from zutils2.lib2.transform2 import Transform2Class

class Trans2Class(Transform2Class):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)
        self.task = Task2Class(input_dict_params)

    def run(self, df=None):
        print("zzz start of combined lib2 Trans1Class method run ===============>")
        super().run(df)
        result1 = self.task.run(df)
        result = str(result1) + '------' + __class__.__name__
        print(f"zzz end of combined lib2 Trans1Class method run ===============>\n {result}")
        return result