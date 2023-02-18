# ############ eval
from zutils1.lib1 import *
from zutils2.lib2 import *
input_df = "df1"
app_input_param = {"zkey4":"zvalue4"}

taks1 = "Task1Class(app_input_param).run(input_df)"
taks2 = "Task2Class(app_input_param).run(input_df)"
taks3 = "Transform1Class(app_input_param).run(input_df)"
taks4 = "Transform2Class(app_input_param).run(input_df)"

etl_work_flow = [taks1,taks2,taks3,taks4]

print("start of ETL dynamic workflow =========================> ", input_df)
for task in etl_work_flow:
    input_df :object = eval(task)

print("End of ETL dynamic workflow ===========> ", input_df)