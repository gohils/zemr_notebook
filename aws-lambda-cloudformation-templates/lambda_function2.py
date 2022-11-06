import botocore
import logging

import json
import urllib.parse
import boto3
import time
import os
import uuid
import datetime
import random
import json

# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG) # Very verbose

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

    print("z1 start lambda_handler")
    
    try:    
        message = get_customer_transaction_Stream()
        msg_str = json.dumps(message) # Convert the message into a JSON string.

        logger.info(msg_str)
    except botocore.exceptions.ClientError as error:
        # Put your error handling logic here
        raise error
        
    return(message)
