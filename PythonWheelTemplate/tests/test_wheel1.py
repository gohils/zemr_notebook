
def test_redshift_module():
    from redshift_module import pygresql_redshift_common as rs_common

    con1 = rs_common.get_connection("redshift_endpoint")
    res = rs_common.query(con1)

    print(res)

def test_data_trans_module():
    from utils.tranformation import data_functions as data_trans
    data_trans.tranform1("df1")
    data_trans.tranform2("df2")

def test_num_trans_module():
    from utils.tranformation import num_functions as num_trans
    num_trans.add_two(25,23)
    num_trans.multiply_two(3,23)

def test_num_validation_module():    
    from utils.validation import num_validation as num_validate
    num_validate.validate1('df1')
    num_validate.validate2('df2')

def test_schema_validation_module():
    from utils.validation import schema_validation as schema_validate
    schema_validate.validate_schema1('df1')
    schema_validate.validate_schema2('df2')