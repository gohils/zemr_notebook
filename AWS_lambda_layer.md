### create layer for event hub -----------------------
mkdir folder
cd folder
python3.7 -m venv myvenv
source myvenv/bin/activate
pip install azure-eventhub
deactivate
mkdir python
cd python
cp -r ../myvenv/lib/python3.7/site-packages/* .
cd ..
zip -r zevent_hub_layer.zip python


pip install --upgrade awscli

aws lambda publish-layer-version --layer-name zevent_hub_layer1 --zip-file fileb://zevent_hub_layer.zip --compatible-runtimes python3.7 python3.8


### create layer for identity managment for service principal
mkdir folder1
cd folder1
python3.7 -m venv myvenv
source myvenv/bin/activate
pip install azure-identity
deactivate
mkdir python
cd python
cp -r ../myvenv/lib/python3.7/site-packages/* .
cd ..
zip -r zazure_identity_layer.zip python


pip install --upgrade awscli

aws lambda publish-layer-version --layer-name zazure_identity_layer1 --zip-file fileb://zazure_identity_layer.zip --compatible-runtimes python3.7 python3.8

#### create new lambda from cloud9
------------------------------
Step 1 — Write the code for the Lambda function.
------------------------------
mkdir zlambda1
cd zlambda1
touch lambda_function.py

------------------------------
# This requests is an external dependency and is used to demonstrate 
# the demo of installing an external dependency in the lambda function.
import requests

#Lambda function execution begins from here.
def lambda_handler(event, context):
    print("Lambda Executed")
    print("This is a demo Lambda function")
    
    return 'hello aws lambda'

-----------------------
Step 2 — install external dependencies for the Lambda function and zip folder for deployment.
-----------------------------
touch requirements.txt
## add external dependencies
requests

NOTE: Here, -t . at the end of the command, indicates that this dependency will be installed only in this folder and not globally in the virtual environment.

Run === pip3 install -r requirements.txt -t .

or installing each one individually

pip install requests -t .

--------------------
test lambda locally
-------------------
touch test_lambda_function.py
## add following
from lambda_function import *
lambda_handler('a','b')

---- run test with python test_lambda_function.py

Now, zip all the files contents within the folder lambda, using the zip command.
NOTE: Here -r *, at the end of command indicates, that all content in this lambda directory will be zipped recursively i.e. one by one.

zip lambda.zip -r *

------------------------------
Step 3 — Create a Lambda function with iam role arn
------------------------------
pip install --upgrade awscli

aws lambda create-function --function-name ztestFunction --runtime python3.9 --role arn:aws:iam::123:role/service-role/zlambda_role1 --zip-file fileb:///home/ec2-user/environment/zlambda1/lambda.zip --handler lambda_function.lambda_handler

