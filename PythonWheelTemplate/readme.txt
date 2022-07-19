# create virtual environment

python -m venv .venv
.venv\Scripts\activate

# create requirements.txt add pip library list 
touch requirements.txt
pip install -r requirements.txt

execute following command to create python package as wheel file
pip install setuptools wheel


python setup.py bdist_wheel

# wheel package file will be created in dist folder 
# copy whl file and pip install it target python