from redshift_module import pygresql_redshift_common as rs_common

con1 = rs_common.get_connection("redshift_endpoint")
res = rs_common.query(con1)

print(res)
      
