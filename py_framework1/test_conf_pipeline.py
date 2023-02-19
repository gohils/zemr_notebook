
# ############ eval
# python test_conf_pipeline.py etl_config_file="./config/etl_pipe1_config.json"
from zutils1.lib1 import *
from zutils2.lib2 import *
import json
import sys

# python test_conf_pipeline.py etl_config_file="./config/etl_pipe1_config.json"
# python test_conf_pipeline.py etl_config_file="./config/etl_pipe2_config.json"

if __name__ == '__main__':

    print((sys.argv[1:]))

    argv = sys.argv[1:]

    kwargs = {kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}
    print("kwargs = ",kwargs )

    input_etl_config_file = kwargs.get('etl_config_file')
    print('zzzzzzzzzzzzzzzzzzz etl_config_file = ',input_etl_config_file)


    with open(input_etl_config_file, 'r') as f:
        etl_json_config = json.load(f)

    input_df = etl_json_config.get('source_table')
    lv_target_table = etl_json_config.get('target_table')
    config_name = etl_json_config.get('config_name')
    config_value = etl_json_config.get('config_value')
    print("start of ETL dynamic workflow =========================> ", input_df)
    result_df = input_df
    for task in etl_json_config.get('task_list'):
        class_name = task.get('classname')
        input_param = task.get('config_details')
        # print(class_name)
        # print(input_param)
        cls2 = eval(class_name)(input_param)
        result_df = cls2.run(result_df)

    print(f"End of ETL dynamic workflow result {lv_target_table}===========> ", result_df)    