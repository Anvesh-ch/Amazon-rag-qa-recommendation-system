"""
Tests for RAG engine functionality.
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from rag_engine import RAGEngine, RAGEngineManager


class TestRAGEngine:
    """Test cases for RAGEngine class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "rag": {
                "top_k": 5,
                "max_input_chars": 3000,
                "generator_model": "google/flan-t5-base",
            },
            "embedding": {"model_name": "sentence-transformers/all-MiniLM-L6-v2"},
        }

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing."""
        return [
            {
                "review_id": "r1",
                "product_id": "p1",
                "product_title": "Great Product",
                "review_body": "This is a great product with excellent quality.",
                "star_rating": 5,
                "category": "Electronics",
                "combined_text": "Great Product This is a great product with excellent quality.",
                "text_length": 50,
                "token_count": 10,
            },
            {
                "review_id": "r2",
                "product_id": "p2",
                "product_title": "Amazing Item",
                "review_body": "Amazing item, highly recommended!",
                "star_rating": 5,
                "category": "Electronics",
                "combined_text": "Amazing Item Amazing item, highly recommended!",
                "text_length": 40,
                "token_count": 8,
            },
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        return np.random.rand(2, 384)  # 384 is the dimension for all-MiniLM-L6-v2

    def test_load_config(self, config):
        """Test configuration loading."""
        with patch("builtins.open", mock_open_config(config)):
            engine = RAGEngine()
            assert engine.config == config

    @patch("rag_engine.SentenceTransformer")
    def test_load_model(self, mock_sentence_transformer, config):
        """Test model loading."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()

            # Mock the model
            mock_model = Mock()
            mock_sentence_transformer.return_value = mock_model

            engine.load_model()

            # Verify model was loaded
            assert engine.model == mock_model
            mock_sentence_transformer.assert_called_once_with(
                config["embedding"]["model_name"]
            )

    @patch("rag_engine.SentenceTransformer")
    def test_generate_embeddings(self, mock_sentence_transformer, config):
        """Test embedding generation."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()

            # Mock the model
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(2, 384)
            mock_sentence_transformer.return_value = mock_model
            engine.model = mock_model

            # Test embedding generation
            texts = ["This is a test", "Another test text"]
            embeddings = engine.generate_embeddings(texts)

            # Verify embeddings shape
            assert embeddings.shape == (2, 384)
            mock_model.encode.assert_called_once()

    @patch("rag_engine.faiss")
    def test_build_faiss_index(self, mock_faiss, config):
        """Test FAISS index building."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()

            # Mock FAISS index
            mock_index = Mock()
            mock_faiss.IndexHNSWFlat.return_value = mock_index

            # Test index building
            embeddings = np.random.rand(10, 384)
            index = engine.build_faiss_index(embeddings, "HNSW")

            # Verify index was created
            assert index == mock_index
            mock_faiss.IndexHNSWFlat.assert_called_once_with(384, 32)
            mock_index.add.assert_called_once()

    def test_ask_question(self, config, sample_metadata):
        """Test question answering functionality."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()

            # Mock the QA chain
            mock_qa_chain = Mock()
            mock_qa_chain.return_value = {
                "result": "This is a test answer",
                "source_documents": [
                    Mock(page_content="Test content 1", metadata=sample_metadata[0]),
                    Mock(page_content="Test content 2", metadata=sample_metadata[1]),
                ],
            }
            engine.qa_chain = mock_qa_chain

            # Test question asking
            result = engine.ask_question("What is the quality like?")

            # Verify result structure
            assert "question" in result
            assert "answer" in result
            assert "sources" in result
            assert "num_sources" in result

            # Verify values
            assert result["question"] == "What is the quality like?"
            assert result["answer"] == "This is a test answer"
            assert result["num_sources"] == 2

    def test_get_similar_reviews(self, config, sample_metadata):
        """Test similar review retrieval."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()

            # Mock vectorstore
            mock_vectorstore = Mock()
            mock_docs = [
                Mock(page_content="Test content 1", metadata=sample_metadata[0]),
                Mock(page_content="Test content 2", metadata=sample_metadata[1]),
            ]
            mock_vectorstore.similarity_search.return_value = mock_docs
            engine.vectorstore = mock_vectorstore

            # Test similar review retrieval
            results = engine.get_similar_reviews("test query", top_k=2)

            # Verify results
            assert len(results) == 2
            assert "content" in results[0]
            assert "metadata" in results[0]
            mock_vectorstore.similarity_search.assert_called_once_with(
                "test query", k=2
            )

    def test_get_engine_stats(self, config):
        """Test engine statistics retrieval."""
        with patch("rag_engine.RAGEngine._load_config", return_value=config):
            engine = RAGEngine()
            engine.metadata = [{"test": "data"}] * 100

            # Test stats retrieval
            stats = engine.get_engine_stats()

            # Verify stats structure
            assert "num_documents" in stats
            assert "model_name" in stats
            assert "embedding_model" in stats
            assert "top_k" in stats
            assert "max_input_chars" in stats

            # Verify values
            assert stats["num_documents"] == 100
            assert stats["model_name"] == config["rag"]["generator_model"]


class TestRAGEngineManager:
    """Test cases for RAGEngineManager class."""

    def test_get_engine(self):
        """Test engine retrieval and creation."""
        manager = RAGEngineManager()

        # Mock RAGEngine
        with patch("rag_engine.RAGEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine

            # Test getting engine
            engine = manager.get_engine("test_path")

            # Verify engine was created and cached
            assert engine == mock_engine
            assert "test_path" in manager.engines
            mock_engine_class.assert_called_once()

    def test_clear_engines(self):
        """Test engine cache clearing."""
        manager = RAGEngineManager()
        manager.engines = {"path1": Mock(), "path2": Mock()}

        # Test clearing engines
        manager.clear_engines()

        # Verify engines were cleared
        assert len(manager.engines) == 0


def mock_open_config(config):
    """Mock open function for config loading."""
    import yaml
    from unittest.mock import mock_open

    config_yaml = yaml.dump(config)
    return mock_open(read_data=config_yaml)


if __name__ == "__main__":
    pytest.main([__file__])
