import sys

# python streaming_reader_with_args.py input_folder="c:\data\zvalue1" sink_folder=\temp\zvalue2 file_type=csv

class StreamingDataPipelineProcess:

    def __init__(self,input_args):
        print("[[[--init streaming pipeline with input argument ------]]]")
        self.input_folder = input_args.get('input_folder')
        self.sink_folder = input_args.get('sink_folder')
        self.file_type = input_args.get('file_type')

        print(input_args)
        pass

    def stream_read(self):
        print("----- start reading stream ///////////")
        print("--------reading from ----------=>",self.input_folder)
        pass
    def stream_data_tranformation(self):
        print("+++++++++++++++ start data transformation of streaming input data +++++++++++++++")
        print("--------transformtion data to ----------=>",self.sink_folder)
        pass
    def stream_output_sink(self):
        print("************ start writing stream result into sink location ************")
        print("--------writing final result with file type ----------=>",self.file_type)
        pass

    def run_stream_pipeline(self):
        print("========= start of main function run_stream_pipeline ===============")
        self.stream_read()
        self.stream_data_tranformation()
        self.stream_output_sink()
        print("========= end of run_stream_pipeline ===============")
        pass


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
 
    # print((sys.argv[1:]))

    argv = sys.argv[1:]
    input_dict = convert_arg_to_dict(argv)
    print('argument input_dict ',input_dict)
    input_value1 = input_dict.get('input_folder')
    # print('value for input_folder = ',input_value1)

    StreamingDataPipelineProcess(input_dict).run_stream_pipeline()

