# -*- coding: utf-8 -*-

"""Core standardizer module."""

from pyspark.sql import DataFrame


def transform(df: DataFrame) -> DataFrame:
    """transform"""
    # Do your transforms here
    return df