import pytest
import os

from pyspark.sql import DataFrame


@pytest.fixture
def spark_session():
    """Spark Session fixture"""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder\
        .master("local[2]")\
        .appName("Unit Testing")\
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark
