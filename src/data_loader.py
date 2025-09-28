"""
Data loader module for Amazon reviews dataset.
Handles loading and basic data operations.
"""

import os
import yaml
from typing import Dict, Any, Optional
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    when,
    isnan,
    isnull,
    regexp_replace,
    trim,
    length,
    split,
    size,
)
from pyspark.sql.types import StringType, IntegerType, DoubleType, BooleanType
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Data loader for Amazon reviews dataset."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize data loader with configuration."""
        self.config = self._load_config(config_path)
        self.spark = self._create_spark_session()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _create_spark_session(self) -> SparkSession:
        """Create Spark session with appropriate configuration."""
        return (
            SparkSession.builder.appName("AmazonReviewsPreprocessing")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .getOrCreate()
        )

    def load_raw_data(self, input_glob: str) -> DataFrame:
        """Load raw data from parquet files."""
        logger.info(f"Loading data from: {input_glob}")

        # Load all parquet files
        df = self.spark.read.option("mergeSchema", "true").parquet(input_glob)

        # Add category column from file path
        df = df.withColumn(
            "category",
            when(col("_metadata.file_path").contains("Apparel"), "Apparel")
            .when(col("_metadata.file_path").contains("Automotive"), "Automotive")
            .when(col("_metadata.file_path").contains("Baby"), "Baby")
            .when(col("_metadata.file_path").contains("Beauty"), "Beauty")
            .when(col("_metadata.file_path").contains("Books"), "Books")
            .when(col("_metadata.file_path").contains("Camera"), "Camera")
            .when(col("_metadata.file_path").contains("Digital_Ebook"), "Digital_Ebook")
            .when(col("_metadata.file_path").contains("Digital_Music"), "Digital_Music")
            .when(
                col("_metadata.file_path").contains("Digital_Software"),
                "Digital_Software",
            )
            .when(col("_metadata.file_path").contains("Digital_Video"), "Digital_Video")
            .when(
                col("_metadata.file_path").contains("Digital_Video_Games"),
                "Digital_Video_Games",
            )
            .when(col("_metadata.file_path").contains("Furniture"), "Furniture")
            .when(col("_metadata.file_path").contains("Gift_Card"), "Gift_Card")
            .when(col("_metadata.file_path").contains("Grocery"), "Grocery")
            .when(
                col("_metadata.file_path").contains("Health_Personal_Care"),
                "Health_Personal_Care",
            )
            .when(
                col("_metadata.file_path").contains("Home_Entertainment"),
                "Home_Entertainment",
            )
            .when(
                col("_metadata.file_path").contains("Home_Improvement"),
                "Home_Improvement",
            )
            .when(col("_metadata.file_path").contains("Home"), "Home")
            .when(col("_metadata.file_path").contains("Jewelry"), "Jewelry")
            .when(col("_metadata.file_path").contains("Kitchen"), "Kitchen")
            .when(
                col("_metadata.file_path").contains("Lawn_and_Garden"),
                "Lawn_and_Garden",
            )
            .when(col("_metadata.file_path").contains("Luggage"), "Luggage")
            .when(
                col("_metadata.file_path").contains("Major_Appliances"),
                "Major_Appliances",
            )
            .when(col("_metadata.file_path").contains("Mobile_Apps"), "Mobile_Apps")
            .when(
                col("_metadata.file_path").contains("Mobile_Electronics"),
                "Mobile_Electronics",
            )
            .when(col("_metadata.file_path").contains("Music"), "Music")
            .when(
                col("_metadata.file_path").contains("Office_Products"),
                "Office_Products",
            )
            .when(col("_metadata.file_path").contains("Outdoors"), "Outdoors")
            .when(col("_metadata.file_path").contains("PC"), "PC")
            .when(
                col("_metadata.file_path").contains("Personal_Care_Appliances"),
                "Personal_Care_Appliances",
            )
            .when(col("_metadata.file_path").contains("Pet_Products"), "Pet_Products")
            .when(col("_metadata.file_path").contains("Shoes"), "Shoes")
            .when(col("_metadata.file_path").contains("Software"), "Software")
            .when(col("_metadata.file_path").contains("Sports"), "Sports")
            .when(col("_metadata.file_path").contains("Tools"), "Tools")
            .when(col("_metadata.file_path").contains("Toys"), "Toys")
            .when(col("_metadata.file_path").contains("Video_DVD"), "Video_DVD")
            .when(col("_metadata.file_path").contains("Video_Games"), "Video_Games")
            .when(col("_metadata.file_path").contains("Video"), "Video")
            .when(col("_metadata.file_path").contains("Watches"), "Watches")
            .when(col("_metadata.file_path").contains("Wireless"), "Wireless")
            .otherwise("Unknown"),
        )

        logger.info(f"Loaded {df.count()} records")
        return df

    def get_sample_data(self, df: DataFrame, n_samples: int = 1000) -> pd.DataFrame:
        """Get a sample of the data for inspection."""
        return df.limit(n_samples).toPandas()

    def get_data_info(self, df: DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset."""
        info = {
            "total_records": df.count(),
            "columns": df.columns,
            "dtypes": dict(df.dtypes),
            "null_counts": {},
        }

        for col_name in df.columns:
            null_count = df.filter(
                col(col_name).isNull() | isnan(col(col_name))
            ).count()
            info["null_counts"][col_name] = null_count

        return info

    def close(self):
        """Close Spark session."""
        if self.spark:
            self.spark.stop()
