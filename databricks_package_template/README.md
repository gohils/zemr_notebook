# pyspark-snippets

This directory contains a number of functions that simplify development of PySpark code for Databricks.

# create virtual environment
python -m venv .venv
.venv\Scripts\activate

1- Building
python setup.py clean --all && python setup.py bdist_wheel --universal

2- Testing
You need to install packages that are necessary for execution of tests:
pip install -r requirements.txt

3- Unit testing
pytest tests/unit
