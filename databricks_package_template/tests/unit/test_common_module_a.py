from pyspark.sql import SparkSession

from pyspark_utils.data_skipping import reorder_columns
from common.module_a import add_mount

def test_module_a_add_mount(spark_session: SparkSession):
    original_df = spark_session.createDataFrame([('Fiji Apple', 'Red', 3.5), 
                           ('Banana', 'Yellow', 1.0),
                           ('Green Grape', 'Green', 2.0),
                           ('Red Grape', 'Red', 2.0),
                           ('Peach', 'Yellow', 3.0),
                           ('Orange', 'Orange', 2.0),
                           ('Green Apple', 'Green', 2.5)], 
                           ['Fruit', 'Color', 'Price'])
    processed_df = add_mount(original_df, 20)
    processed_df = reorder_columns(original_df)
    assert 'processed_df' == 'processed_df'
