from zutils1.lib1.mod1 import Task1Class
from zutils2.lib2.transform1 import Transform1Class

class Trans1Class(Transform1Class):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)
        self.task = Task1Class(input_dict_params)

    def run(self, df=None):
        print("zzz start of combined lib2 Trans1Class method run ===============>")
        super().run(df)
        result1 = self.task.run(df)
        result = str(result1) + '------' + __class__.__name__
        print(f"zzz end of combined lib2 Trans1Class method run ===============>\n {result}")
        return result