import json
import urllib.parse
import boto3
import time
import os
import uuid
import datetime
import random
import json

print('Loading function')

s3 = boto3.client('s3')

def get_customer_transaction_Stream():
    data = {}
    now = datetime.datetime.now()
    str_now = now.isoformat()
    data['transaction_id'] = str(uuid.uuid4())
    data['store_id'] = random.choice(['store1','store2', 'store3', 'store4'])
    data['customer_number'] = random.randint(21000,29999)
    data['product_number'] = random.choice(['Burger','Pizza','Pasta', 'IceCream','Juice','Chips'])
    data['sold_quantity'] = random.randint(1,5)
    data['customer_total_spent'] = random.randint(20,100)
    data['customer_state'] = random.choice(['NSW','VIC', 'QLD', 'WA','SA','NT'])
    data['transaction_time'] = str_now
    return data
    
def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    message = get_customer_transaction_Stream()
    msg_str = json.dumps(message) # Convert the message into a JSON string.
    s3.put_object(Bucket='zs3-test1', Key='test1.txt',Body=msg_str)
    
    print('Original object from the S3 bucket:')
    original = s3.get_object(
      Bucket='zs3-test1',
      Key='test1.txt')
      
    file_data = original['Body'].read().decode('utf-8')
    
    print('Object processed by S3 Object Lambda: -----',file_data)

    return file_data
