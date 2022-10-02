Lambda Function Code:
-----------------------------------------
import json
import requests
import uuid
import boto3
s3 = boto3.client('s3')
limit=1000


def lambda_handler(event, context):
    print(event)
    offset=0
    body=event.get("body",0)
    if body==0:
        offset=0
    else:
        offset=event['body']["offset"]
        
    isComplete=False
    url="http://jsonplaceholder.typicode.com/p...{}&_limit={}".format(offset,limit)
    
    print("URL for the current iteration : {}".format(url))
    
    result=requests.get(url);
    data_extracted=result.json();
    
    length_of_no_of_records_extracted_now=len(data_extracted)
    
    if(length_of_no_of_records_extracted_now!=0):
        file_name="{Folder Name}/"+str(uuid.uuid4())+".json"
        s3.put_object(
        Body=json.dumps(data_extracted),
        Bucket='{Bucket Name}',
        Key=file_name
        )
    
    if(length_of_no_of_records_extracted_now==0):
        isComplete=True
          
    offset=offset+limit
    
    response_json_set={'offset':offset,
                        'isComplete':isComplete
                        }
    
    
        
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': response_json_set
    }