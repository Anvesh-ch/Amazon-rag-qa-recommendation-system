"""
Pytest configuration and shared fixtures.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "preprocess": {
            "input_glob": "data/raw/*/*.parquet",
            "output_parquet": "data/processed/reviews_clean.parquet",
            "output_sample_for_eda": "data/exports/eda_sample.parquet",
            "mode": "stratified_sample",
            "verified_only": True,
            "min_tokens": 3,
            "max_chars": 4000,
            "text_fields": ["review_body", "product_title"],
            "sampling": {
                "seed": 42,
                "target_rows_total": 100000,
                "stratify_by": "star_rating",
                "per_category_cap": 25000,
                "fraction_floor": 0.02,
            },
            "eda_export": {"rows": 20000},
        },
        "embedding": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "batch_size": 64,
            "normalize": True,
            "index_type": "HNSW",
            "output_path": "data/embeddings/",
        },
        "rag": {
            "top_k": 5,
            "max_input_chars": 3000,
            "generator_model": "google/flan-t5-base",
        },
        "recommend": {"top_k": 10, "min_similarity": 0.3},
        "api": {"host": "0.0.0.0", "port": 8000},
        "ui": {"streamlit_port": 8501},
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return [
        {
            "review_id": "r1",
            "product_id": "p1",
            "product_title": "Great Wireless Headphones",
            "review_body": "These headphones have excellent sound quality and great battery life.",
            "star_rating": 5,
            "verified_purchase": True,
            "category": "Electronics",
            "review_date": "2023-01-15",
            "reviewer_id": "user1",
        },
        {
            "review_id": "r2",
            "product_id": "p2",
            "product_title": "Amazing Smartphone",
            "review_body": "Love this phone! Camera is fantastic and performance is smooth.",
            "star_rating": 5,
            "verified_purchase": True,
            "category": "Electronics",
            "review_date": "2023-02-20",
            "reviewer_id": "user2",
        },
        {
            "review_id": "r3",
            "product_id": "p3",
            "product_title": "Good Book",
            "review_body": "Interesting read, well written and engaging.",
            "star_rating": 4,
            "verified_purchase": True,
            "category": "Books",
            "review_date": "2023-03-10",
            "reviewer_id": "user3",
        },
        {
            "review_id": "r4",
            "product_id": "p4",
            "product_title": "Poor Quality Item",
            "review_body": "Not worth the money. Broke after a week.",
            "star_rating": 2,
            "verified_purchase": True,
            "category": "Electronics",
            "review_date": "2023-04-05",
            "reviewer_id": "user4",
        },
        {
            "review_id": "r5",
            "product_id": "p5",
            "product_title": "Excellent Laptop",
            "review_body": "Fast, reliable, and great for work. Highly recommended!",
            "star_rating": 5,
            "verified_purchase": True,
            "category": "Electronics",
            "review_date": "2023-05-12",
            "reviewer_id": "user5",
        },
    ]


@pytest.fixture
def sample_embeddings():
    """Sample embeddings for testing."""
    import numpy as np

    return np.random.rand(5, 384)  # 384 is the dimension for all-MiniLM-L6-v2


@pytest.fixture
def mock_spark_session():
    """Mock Spark session for testing."""
    mock_session = Mock()
    mock_session.read.option.return_value.parquet.return_value = Mock()
    mock_session.stop.return_value = None
    return mock_session


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer for testing."""
    mock_model = Mock()
    mock_model.encode.return_value = np.random.rand(2, 384)
    return mock_model


@pytest.fixture
def mock_faiss_index():
    """Mock FAISS index for testing."""
    mock_index = Mock()
    mock_index.ntotal = 1000
    mock_index.search.return_value = (
        np.array([[0.1, 0.2, 0.3]]),
        np.array([[0, 1, 2]]),
    )
    return mock_index


@pytest.fixture
def mock_llm():
    """Mock language model for testing."""
    mock_llm = Mock()
    mock_llm.return_value = "This is a test answer"
    return mock_llm


@pytest.fixture
def mock_qa_chain():
    """Mock QA chain for testing."""
    mock_chain = Mock()
    mock_chain.return_value = {
        "result": "This is a test answer based on the provided context.",
        "source_documents": [
            Mock(
                page_content="Test content 1",
                metadata={"product_title": "Test Product 1"},
            ),
            Mock(
                page_content="Test content 2",
                metadata={"product_title": "Test Product 2"},
            ),
        ],
    }
    return mock_chain


@pytest.fixture
def mock_vectorstore():
    """Mock vectorstore for testing."""
    mock_vs = Mock()
    mock_vs.similarity_search.return_value = [
        Mock(
            page_content="Test content 1", metadata={"product_title": "Test Product 1"}
        ),
        Mock(
            page_content="Test content 2", metadata={"product_title": "Test Product 2"}
        ),
    ]
    mock_vs.as_retriever.return_value = Mock()
    return mock_vs


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(
            marker.name in ["slow", "integration"] for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)
