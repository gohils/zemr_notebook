from zutils2.lib2.transform_base import TransformBaseClass

class Transform2Class(TransformBaseClass):
    def __init__(self, input_dict_params=None):
        super().__init__(input_dict_params)

    def run(self, df=None):
        print("zzz lib2 Transform2Class method run is executed")
        print(f"zzz self.input_params is {self.input_params}")
        result = str(df) + '------' + __class__.__name__
        return result