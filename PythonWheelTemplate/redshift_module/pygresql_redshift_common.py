


def get_connection(host):
    print("get_connection for host ",str(host))
    return host


def query(con):
    statement = f"Select * from table_name; for connection - {con}"
    return statement
    
