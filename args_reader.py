import json
import sys
import getopt
import time
import os
import argparse

# python args_reader.py --shard=zshard --token=5555 --clusterid=zclid12345 --libs=zlib --dbfspath=zdbfs://path/lib.whl
# python args_reader.py --clusterid=zclid12345 --libs=zlib --dbfspath=zdbfs://path/lib.whl --shard=zshard --token=5555 
def read_data():
    print("read data")
    print('--shard is ' + gv_shard)
    result = f'shard= {gv_shard} token= {gv_token}  clusterid= {gv_clusterid}  dbfspath= {gv_dbfspath}'
    print(result)

def trasform_data():
    print("trasform_data")
    result = f'shard= {gv_shard} token= {gv_token}  clusterid= {gv_clusterid}  dbfspath= {gv_dbfspath}'
    print(result)

def write_result_data():
    print("write_result_data")
    result = f'shard= {gv_shard} token= {gv_token}  clusterid= {gv_clusterid}  dbfspath= {gv_dbfspath}'
    print(result)

def main():
    # initialize Global Variables
    global gv_shard, gv_token, gv_clusterid, gv_libspath, gv_dbfspath

    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:t:c:l:d',
                                   ['shard=', 'token=', 'clusterid=', 'libs=', 'dbfspath='])
    except getopt.GetoptError as err:
        print(err)
        print('exception raised -s <shard> -t <token> -c <clusterid> -l <libs> -d <dbfspath>')
        sys.exit(2)

    # print(opts)
    # print(args)
    
    for opt, arg in opts:
        if opt == '-h':
            print('exception raised -s <shard> -t <token> -c <clusterid> -l <libs> -d <dbfspath>')
            sys.exit()
        elif opt in ('-s', '--shard'):
            gv_shard = arg
        elif opt in ('-t', '--token'):
            gv_token = arg
        elif opt in ('-c', '--clusterid'):
            gv_clusterid = arg
        elif opt in ('-l', '--libs'):
            gv_libspath=arg
        elif opt in ('-d', '--dbfspath'):
            gv_dbfspath=arg

    # check all arg variables are populated/passed
    if None not in (gv_shard, gv_token, gv_clusterid, gv_libspath, gv_dbfspath):
        pass

    print('--shard is ' + gv_shard)
    print('--token is ' + gv_token)
    print('--clusterid is ' + gv_clusterid)
    print('--libspath is ' + gv_libspath)
    print('--dbfspath is ' + gv_dbfspath)

    read_data()
    trasform_data()
    write_result_data()


if __name__ == '__main__':
    main()    