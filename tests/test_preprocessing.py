"""
Tests for text preprocessing pipeline.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from text_preprocess import TextPreprocessor
from data_loader import DataLoader


class TestTextPreprocessor:
    """Test cases for TextPreprocessor class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame(
            {
                "review_id": ["r1", "r2", "r3", "r4", "r5"],
                "product_id": ["p1", "p2", "p3", "p4", "p5"],
                "product_title": [
                    "Great Product",
                    "Amazing Item",
                    "Good Stuff",
                    "Bad Product",
                    "Excellent",
                ],
                "review_body": [
                    "This is a great product with excellent quality.",
                    "Amazing item, highly recommended!",
                    "Good stuff, works as expected.",
                    "Bad product, poor quality.",
                    "Excellent product, love it!",
                ],
                "star_rating": [5, 5, 4, 2, 5],
                "verified_purchase": [True, True, True, True, True],
                "category": [
                    "Electronics",
                    "Electronics",
                    "Books",
                    "Electronics",
                    "Books",
                ],
            }
        )

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "preprocess": {
                "verified_only": True,
                "min_tokens": 3,
                "max_chars": 1000,
                "text_fields": ["review_body", "product_title"],
                "sampling": {
                    "seed": 42,
                    "target_rows_total": 1000,
                    "stratify_by": "star_rating",
                    "per_category_cap": 100,
                },
            }
        }

    def test_clean_text(self, sample_data, config):
        """Test text cleaning functionality."""
        with patch(
            "text_preprocess.TextPreprocessor._load_config", return_value=config
        ):
            preprocessor = TextPreprocessor()

            # Mock Spark DataFrame
            mock_df = Mock()
            mock_df.withColumn.return_value = mock_df
            mock_df.filter.return_value = mock_df
            mock_df.count.return_value = 5

            # Test text cleaning
            result = preprocessor.clean_text(mock_df)

            # Verify that withColumn was called for text cleaning
            assert mock_df.withColumn.call_count >= 3  # At least 3 new columns created

    def test_apply_filters(self, sample_data, config):
        """Test filtering functionality."""
        with patch(
            "text_preprocess.TextPreprocessor._load_config", return_value=config
        ):
            preprocessor = TextPreprocessor()

            # Mock Spark DataFrame
            mock_df = Mock()
            mock_df.filter.return_value = mock_df
            mock_df.count.return_value = 5
            mock_df.dropDuplicates.return_value = mock_df

            # Test filtering
            result = preprocessor.apply_filters(mock_df)

            # Verify that filter was called
            assert mock_df.filter.call_count >= 1
            assert mock_df.dropDuplicates.call_count == 1

    def test_stratified_sampling(self, sample_data, config):
        """Test stratified sampling functionality."""
        with patch(
            "text_preprocess.TextPreprocessor._load_config", return_value=config
        ):
            preprocessor = TextPreprocessor()

            # Mock Spark DataFrame
            mock_df = Mock()
            mock_df.groupBy.return_value.count.return_value.collect.return_value = [
                Mock(category="Electronics", count=3),
                Mock(category="Books", count=2),
            ]
            mock_df.count.return_value = 5
            mock_df.filter.return_value = mock_df
            mock_df.sample.return_value = mock_df
            mock_df.union.return_value = mock_df

            # Test stratified sampling
            result = preprocessor.stratified_sampling(mock_df)

            # Verify that sampling methods were called
            assert mock_df.groupBy.call_count == 1

    def test_get_preprocessing_stats(self, sample_data, config):
        """Test preprocessing statistics calculation."""
        with patch(
            "text_preprocess.TextPreprocessor._load_config", return_value=config
        ):
            preprocessor = TextPreprocessor()

            # Mock DataFrames
            original_df = Mock()
            original_df.count.return_value = 1000

            processed_df = Mock()
            processed_df.count.return_value = 500
            processed_df.select.return_value.distinct.return_value.collect.return_value = [
                Mock(category="Electronics"),
                Mock(category="Books"),
            ]
            processed_df.groupBy.return_value.count.return_value.collect.return_value = [
                Mock(star_rating=5, count=200),
                Mock(star_rating=4, count=150),
                Mock(star_rating=3, count=100),
                Mock(star_rating=2, count=30),
                Mock(star_rating=1, count=20),
            ]
            processed_df.select.return_value.rdd.map.return_value.mean.return_value = (
                50.0
            )

            # Test stats calculation
            stats = preprocessor.get_preprocessing_stats(original_df, processed_df)

            # Verify stats structure
            assert "original_count" in stats
            assert "processed_count" in stats
            assert "reduction_ratio" in stats
            assert "categories" in stats
            assert "star_rating_distribution" in stats
            assert "avg_text_length" in stats
            assert "avg_token_count" in stats

            # Verify values
            assert stats["original_count"] == 1000
            assert stats["processed_count"] == 500
            assert stats["reduction_ratio"] == 0.5


class TestDataLoader:
    """Test cases for DataLoader class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {"preprocess": {"input_glob": "test_data/*.parquet"}}

    def test_load_config(self, config):
        """Test configuration loading."""
        with patch("builtins.open", mock_open_config(config)):
            loader = DataLoader()
            assert loader.config == config

    def test_create_spark_session(self, config):
        """Test Spark session creation."""
        with patch("data_loader.DataLoader._load_config", return_value=config):
            with patch("pyspark.sql.SparkSession.builder") as mock_builder:
                mock_session = Mock()
                mock_builder.appName.return_value = mock_builder
                mock_builder.config.return_value = mock_builder
                mock_builder.getOrCreate.return_value = mock_session

                loader = DataLoader()
                assert loader.spark == mock_session


def mock_open_config(config):
    """Mock open function for config loading."""
    import yaml
    from unittest.mock import mock_open

    config_yaml = yaml.dump(config)
    return mock_open(read_data=config_yaml)


if __name__ == "__main__":
    pytest.main([__file__])
