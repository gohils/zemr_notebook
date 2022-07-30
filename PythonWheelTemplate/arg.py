import sys

# python arg.py 1 2 zkey1="c:\data\zvalue1" zkey2=\temp\zvalue2
# python arg.py input_folder="c:\data\zvalue1" sink_folder=\temp\zvalue2 file_type=csv

def convert_arg_to_dict(arg_list):
    output = []
    for key_value in arg_list:
        key, value = key_value.split('=', 1)
        if not output or key in output[-1]:
            output.append({})
        output[-1][key] = value
    print(output)
    return output[0]

if __name__ == '__main__':
    # function1(**input)

    print((sys.argv[1:]))

    argv = sys.argv[1:]
    input_dict = convert_arg_to_dict(argv)
    print('argument input_dict ',input_dict)
    input_value1 = input_dict.get('input_folder')
    print('value for input_folder = ',input_value1)

    kwargs = {kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}

    print("kwargs = ",kwargs )

    input_value1 = kwargs.get('input_folder')
    print('value for input_folder = ',input_value1)
    input_value2 = kwargs.get('sink_folder')
    print('value for sink_folder = ',input_value2)
    input_value3 = kwargs.get('file_type')
    print('value for sink_folder = ',input_value3)

    input_args = sys.argv[1]
    print(input_args)