"""
Text preprocessing module using PySpark.
Handles cleaning, filtering, and stratified sampling of Amazon reviews.
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Tuple
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
    lit,
    rand,
    row_number,
    sum as spark_sum,
    count as spark_count,
    collect_list,
    first,
    last,
)
from pyspark.sql.types import StringType, IntegerType, DoubleType, BooleanType
from pyspark.sql.window import Window
import pandas as pd

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Text preprocessor for Amazon reviews using PySpark."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize preprocessor with configuration."""
        self.config = self._load_config(config_path)
        self.spark = self._create_spark_session()
        self.preprocess_config = self.config["preprocess"]

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _create_spark_session(self) -> SparkSession:
        """Create Spark session with appropriate configuration."""
        return (
            SparkSession.builder.appName("AmazonReviewsTextPreprocessing")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .getOrCreate()
        )

    def clean_text(self, df: DataFrame) -> DataFrame:
        """Clean and preprocess text fields."""
        logger.info("Starting text cleaning...")

        # Clean review_body
        df = df.withColumn(
            "review_body_clean",
            when(
                col("review_body").isNotNull(),
                regexp_replace(
                    regexp_replace(
                        regexp_replace(
                            trim(col("review_body")),
                            r"[^\w\s.,!?;:\-()]",
                            "",  # Remove special chars except basic punctuation
                        ),
                        r"\s+",
                        " ",  # Replace multiple spaces with single space
                    ),
                    r"^\s*$",
                    "",  # Replace empty strings
                ),
            ).otherwise(""),
        )

        # Clean product_title
        df = df.withColumn(
            "product_title_clean",
            when(
                col("product_title").isNotNull(),
                regexp_replace(
                    regexp_replace(
                        regexp_replace(
                            trim(col("product_title")), r"[^\w\s.,!?;:\-()]", ""
                        ),
                        r"\s+",
                        " ",
                    ),
                    r"^\s*$",
                    "",
                ),
            ).otherwise(""),
        )

        # Combine text fields
        df = df.withColumn(
            "combined_text",
            when(
                col("review_body_clean") != "" & col("product_title_clean") != "",
                col("product_title_clean") + " " + col("review_body_clean"),
            )
            .when(col("review_body_clean") != "", col("review_body_clean"))
            .when(col("product_title_clean") != "", col("product_title_clean"))
            .otherwise(""),
        )

        # Calculate text length and token count
        df = df.withColumn("text_length", length(col("combined_text")))
        df = df.withColumn("token_count", size(split(col("combined_text"), " ")))

        logger.info("Text cleaning completed")
        return df

    def apply_filters(self, df: DataFrame) -> DataFrame:
        """Apply filtering criteria."""
        logger.info("Applying filters...")

        # Verified purchases only
        if self.preprocess_config.get("verified_only", True):
            df = df.filter(col("verified_purchase") == True)
            logger.info("Applied verified purchase filter")

        # Text length filters
        min_tokens = self.preprocess_config.get("min_tokens", 3)
        max_chars = self.preprocess_config.get("max_chars", 4000)

        df = df.filter(
            (col("token_count") >= min_tokens)
            & (col("text_length") <= max_chars)
            & (col("combined_text") != "")
        )

        # Remove duplicates based on review_id
        df = df.dropDuplicates(["review_id"])

        logger.info(f"After filtering: {df.count()} records")
        return df

    def stratified_sampling(self, df: DataFrame) -> DataFrame:
        """Perform stratified sampling by star rating and category."""
        logger.info("Starting stratified sampling...")

        sampling_config = self.preprocess_config.get("sampling", {})
        target_rows = sampling_config.get("target_rows_total", 100000)
        stratify_by = sampling_config.get("stratify_by", "star_rating")
        per_category_cap = sampling_config.get("per_category_cap", 25000)
        seed = sampling_config.get("seed", 42)

        # Get category distribution
        category_counts = df.groupBy("category").count().collect()
        total_records = df.count()

        logger.info(f"Total records before sampling: {total_records}")
        logger.info(f"Categories found: {[row.category for row in category_counts]}")

        # Calculate sampling fractions per category
        sampling_fractions = {}
        for row in category_counts:
            category = row.category
            count = row.count
            # Cap per category
            capped_count = min(count, per_category_cap)
            fraction = min(capped_count / count, 1.0)
            sampling_fractions[category] = fraction
            logger.info(
                f"Category {category}: {count} records, sampling fraction: {fraction:.4f}"
            )

        # Apply stratified sampling
        sampled_dfs = []
        for category, fraction in sampling_fractions.items():
            if fraction > 0:
                category_df = df.filter(col("category") == category)
                if fraction < 1.0:
                    category_sample = category_df.sample(fraction=fraction, seed=seed)
                else:
                    category_sample = category_df
                sampled_dfs.append(category_sample)

        # Union all sampled dataframes
        if sampled_dfs:
            result_df = sampled_dfs[0]
            for df_sample in sampled_dfs[1:]:
                result_df = result_df.union(df_sample)
        else:
            result_df = df

        # If we still have too many records, do additional random sampling
        final_count = result_df.count()
        if final_count > target_rows:
            final_fraction = target_rows / final_count
            result_df = result_df.sample(fraction=final_fraction, seed=seed)
            logger.info(f"Applied additional random sampling: {final_fraction:.4f}")

        logger.info(f"Final sampled records: {result_df.count()}")
        return result_df

    def single_category_sampling(self, df: DataFrame) -> DataFrame:
        """Sample data from a single category."""
        single_category = self.preprocess_config.get(
            "single_category", "Lawn and Garden"
        )
        logger.info(f"Sampling from single category: {single_category}")

        df = df.filter(col("category") == single_category)
        logger.info(f"Records in {single_category}: {df.count()}")

        return df

    def create_eda_sample(self, df: DataFrame) -> DataFrame:
        """Create a sample for EDA."""
        eda_config = self.preprocess_config.get("eda_export", {})
        eda_rows = eda_config.get("rows", 20000)

        logger.info(f"Creating EDA sample with {eda_rows} rows")

        # Stratified sample for EDA
        eda_sample = df.sample(fraction=min(eda_rows / df.count(), 1.0), seed=42)

        return eda_sample

    def preprocess(self, input_glob: str) -> Tuple[DataFrame, DataFrame]:
        """Complete preprocessing pipeline."""
        logger.info("Starting preprocessing pipeline...")

        # Load data
        from .data_loader import DataLoader

        loader = DataLoader()
        df = loader.load_raw_data(input_glob)

        # Clean text
        df = self.clean_text(df)

        # Apply filters
        df = self.apply_filters(df)

        # Apply sampling strategy
        mode = self.preprocess_config.get("mode", "stratified_sample")
        if mode == "single_category":
            df = self.single_category_sampling(df)
        elif mode == "stratified_sample":
            df = self.stratified_sampling(df)
        # For 'full' mode, use all data

        # Create EDA sample
        eda_sample = self.create_eda_sample(df)

        logger.info("Preprocessing pipeline completed")
        return df, eda_sample

    def save_processed_data(self, df: DataFrame, eda_sample: DataFrame):
        """Save processed data to parquet files."""
        logger.info("Saving processed data...")

        # Create output directories
        os.makedirs(
            os.path.dirname(self.preprocess_config["output_parquet"]), exist_ok=True
        )
        os.makedirs(
            os.path.dirname(self.preprocess_config["output_sample_for_eda"]),
            exist_ok=True,
        )

        # Save main processed data
        df.write.mode("overwrite").parquet(self.preprocess_config["output_parquet"])
        logger.info(
            f"Saved processed data to: {self.preprocess_config['output_parquet']}"
        )

        # Save EDA sample
        eda_sample.write.mode("overwrite").parquet(
            self.preprocess_config["output_sample_for_eda"]
        )
        logger.info(
            f"Saved EDA sample to: {self.preprocess_config['output_sample_for_eda']}"
        )

    def get_preprocessing_stats(
        self, original_df: DataFrame, processed_df: DataFrame
    ) -> Dict[str, Any]:
        """Get statistics about the preprocessing."""
        stats = {
            "original_count": original_df.count(),
            "processed_count": processed_df.count(),
            "reduction_ratio": processed_df.count() / original_df.count(),
            "categories": [
                row.category
                for row in processed_df.select("category").distinct().collect()
            ],
            "star_rating_distribution": dict(
                processed_df.groupBy("star_rating").count().collect()
            ),
            "avg_text_length": processed_df.select("text_length")
            .rdd.map(lambda x: x[0])
            .mean(),
            "avg_token_count": processed_df.select("token_count")
            .rdd.map(lambda x: x[0])
            .mean(),
        }

        return stats

    def close(self):
        """Close Spark session."""
        if self.spark:
            self.spark.stop()


def main():
    """Main function for running preprocessing pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Preprocess Amazon reviews data")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--input", help="Input data glob pattern")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize preprocessor
    preprocessor = TextPreprocessor(args.config)

    try:
        # Get input glob from args or config
        input_glob = args.input or preprocessor.preprocess_config["input_glob"]

        # Run preprocessing
        processed_df, eda_sample = preprocessor.preprocess(input_glob)

        # Save results
        preprocessor.save_processed_data(processed_df, eda_sample)

        # Print statistics
        original_df = preprocessor.spark.read.option("mergeSchema", "true").parquet(
            input_glob
        )
        stats = preprocessor.get_preprocessing_stats(original_df, processed_df)

        print("\n=== Preprocessing Statistics ===")
        print(f"Original records: {stats['original_count']:,}")
        print(f"Processed records: {stats['processed_count']:,}")
        print(f"Reduction ratio: {stats['reduction_ratio']:.2%}")
        print(f"Categories: {stats['categories']}")
        print(f"Average text length: {stats['avg_text_length']:.1f} characters")
        print(f"Average token count: {stats['avg_token_count']:.1f} tokens")

    finally:
        preprocessor.close()


if __name__ == "__main__":
    main()
