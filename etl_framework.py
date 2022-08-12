
class EtlBase:
    def __init__(self):
        pass

    def run(self):
        pass

class Extract(EtlBase):
    def __init__(self,input_dataframe,input_dict_params=None):
        super().__init__()
        self.input_df = input_dataframe
        self.input_params = input_dict_params
        # print("init from extract")        

    def run(self):
        print("run Extract")
        result = str(self.input_df) + '_Extract'
        return result    

class Transform1(EtlBase):
    def __init__(self,input_dataframe,input_dict_params=None):
        super().__init__()
        self.input_df = input_dataframe
        self.input_params = input_dict_params
        # print("init from Transform1")        

    def run(self):
        print("run Transform1")
        result = str(self.input_df) + '_Transform1'
        return result    

class Transform2(EtlBase):
    def __init__(self,input_dataframe,input_dict_params=None):
        super().__init__()
        self.input_df = input_dataframe
        self.input_params = input_dict_params
        # print("init from Transform2")        

    def run(self):
        print("run Transform2")
        result = str(self.input_df) + '_Transform2'
        return result    

class Load(EtlBase):
    def __init__(self,input_dataframe,input_dict_params=None):
        super().__init__()
        self.input_df = input_dataframe
        self.input_params = input_dict_params
        # print("init from Load")        

    def run(self):
        print("run Load")
        result = str(self.input_df) + '_Load'
        return result    

input_df = "df1"
app_input_param ="zparams1"

result = Extract(input_dataframe=input_df,input_dict_params=app_input_param).run()
print(result)

taks1 = "Extract(input_dataframe=input_df,input_dict_params=app_input_param).run()"
taks2 = "Transform1(input_dataframe=input_df,input_dict_params=app_input_param).run()"
taks3 = "Transform2(input_dataframe=input_df,input_dict_params=app_input_param).run()"
taks4 = "Load(input_dataframe=input_df,input_dict_params=app_input_param).run()"

etl_work_flow = [taks1,taks2,taks3,taks4]

print("start of ETL workflow ====> ", input_df)
for task in etl_work_flow:
    input_df :object = eval(task)

print("End of ETL workflow ====> ", input_df)


import json
import os
# {"extract":"input_file_process","transform":["tranform1","transform2"], "load" : "output_path"}
json_str = {"extract":"Extract(input_dataframe=input_df,input_dict_params=app_input_param).run()",
"transform":["Transform1(input_dataframe=input_df,input_dict_params=app_input_param).run()",
"Transform2(input_dataframe=input_df,input_dict_params=app_input_param).run()"], 
"load" : "Load(input_dataframe=input_df,input_dict_params=app_input_param).run()"}

file_path = './etl_pipe1_config.json'
with open(file_path,'w') as file:
    json.dump(json_str,file)

configJson = open(file_path,'r')
config_dict = json.load(configJson)

# print(config_dict)
# print(type(config_dict))

tasks_list = []
tasks_list.append(config_dict['extract'])
tasks_list = tasks_list + config_dict['transform']
tasks_list.append(config_dict['load'])

input_df = "df1"
app_input_param ="zparams1"
print("start of ETL json workflow =***********************> ", input_df)
for task in tasks_list:
    input_df :object = eval(task)

print("End of ETL json workflow =***********************> ", input_df)