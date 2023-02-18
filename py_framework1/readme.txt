# create virtual environment

python -m venv .venv
.venv\Scripts\activate

pip install setuptools wheel
pip install -r requirements.txt 
create setup.py
python setup.py sdist bdist_wheel

pip list
The following is need to install library locally to avoid module not found error
pip install -e .

---- download python wheel dependecies from pypi to local dir
pip wheel -r requirements.txt --wheel-dir=./wheelhouse 
---- install python wheel dependecies from local wheels dir
pip install -r requirements.txt --no-index --find-links=./wheelhouse 

------ list all install package into requirement files
pip freeze > ./wheelhouse/requirements.txt
------ uninstall all python lib 
pip uninstall -r ./wheelhouse/requirements.txt -y

pip list


# create requirements.txt add pip library list 
touch requirements.txt
pip install -r requirements.txt

execute following command to create python package as wheel file
run pytest -v
pip install setuptools wheel
python setup.py sdist bdist_wheel

# run bdist_wheel option to generate whl file into dist folder which can be install with pip install command
python setup.py bdist_wheel

# wheel package file data_framework-0.1.1-py3-none-any.whl will be created in dist folder 
# copy whl file and pip install data_framework-0.1.1-py3-none-any.whl at target python app


pip install --no-index --find-links=./wheels -r ./wheels/requirements.txt
pip wheel --wheel-dir=./wheels -r requirements.txt

pip freeze > ./wheels/requirements.txt

pip uninstall -r ./wheels/requirements.txt

pip list