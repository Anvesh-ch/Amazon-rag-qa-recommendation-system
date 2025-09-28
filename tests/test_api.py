"""
Tests for FastAPI endpoints.
"""

import pytest
import requests
import json
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from api.main import app
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_question_response(self):
        """Sample question response."""
        return {
            "question": "What do customers say about product quality?",
            "answer": "Customers generally praise the product quality.",
            "sources": [
                {
                    "content": "Great quality product!",
                    "metadata": {
                        "product_title": "Test Product",
                        "star_rating": 5,
                        "category": "Electronics",
                    },
                }
            ],
            "num_sources": 1,
        }

    @pytest.fixture
    def sample_recommendation_response(self):
        """Sample recommendation response."""
        return {
            "recommendations": [
                {
                    "product_id": "p1",
                    "product_title": "Test Product 1",
                    "category": "Electronics",
                    "similarity_score": 0.85,
                    "average_rating": 4.5,
                    "num_reviews": 100,
                    "review_snippets": ["Great product!", "Highly recommended!"],
                    "rationale": "High similarity and positive reviews",
                }
            ],
            "query_type": "text_query",
            "total_found": 1,
        }

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Amazon Review RAG QA + Recommender API" in data["message"]

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch("api.routers.ask_review.get_rag_engine")
    def test_ask_question_endpoint(
        self, mock_get_rag_engine, client, sample_question_response
    ):
        """Test ask question endpoint."""
        # Mock RAG engine
        mock_engine = Mock()
        mock_engine.ask_question.return_value = sample_question_response
        mock_get_rag_engine.return_value = mock_engine

        # Test question asking
        response = client.post(
            "/ask_review/ask",
            json={
                "question": "What do customers say about product quality?",
                "max_sources": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["question"] == sample_question_response["question"]
        assert data["answer"] == sample_question_response["answer"]
        assert data["num_sources"] == sample_question_response["num_sources"]

    @patch("api.routers.recommend.get_recommender")
    def test_recommend_products_endpoint(
        self, mock_get_recommender, client, sample_recommendation_response
    ):
        """Test product recommendation endpoint."""
        # Mock recommender
        mock_recommender = Mock()
        mock_recommender.get_similar_products.return_value = (
            sample_recommendation_response["recommendations"]
        )
        mock_get_recommender.return_value = mock_recommender

        # Test product recommendation
        response = client.post(
            "/recommend/products",
            json={"query": "wireless headphones", "top_k": 10, "min_similarity": 0.3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "text_query"
        assert data["total_found"] == 1
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["product_id"] == "p1"

    @patch("api.routers.recommend.get_recommender")
    def test_recommend_by_product_endpoint(
        self, mock_get_recommender, client, sample_recommendation_response
    ):
        """Test recommendation by product ID endpoint."""
        # Mock recommender
        mock_recommender = Mock()
        mock_recommender.recommend_by_product.return_value = (
            sample_recommendation_response["recommendations"]
        )
        mock_get_recommender.return_value = mock_recommender

        # Test recommendation by product
        response = client.post(
            "/recommend/products", json={"product_id": "p1", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "product_similar"
        assert data["total_found"] == 1

    @patch("api.routers.recommend.get_recommender")
    def test_recommend_by_category_endpoint(
        self, mock_get_recommender, client, sample_recommendation_response
    ):
        """Test recommendation by category endpoint."""
        # Mock recommender
        mock_recommender = Mock()
        mock_recommender.get_category_recommendations.return_value = (
            sample_recommendation_response["recommendations"]
        )
        mock_get_recommender.return_value = mock_recommender

        # Test recommendation by category
        response = client.post(
            "/recommend/products", json={"category": "Electronics", "top_k": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "category_top"
        assert data["total_found"] == 1

    def test_ask_question_validation(self, client):
        """Test question validation."""
        # Test empty question
        response = client.post("/ask_review/ask", json={"question": ""})
        assert response.status_code == 422  # Validation error

    def test_recommend_validation(self, client):
        """Test recommendation validation."""
        # Test missing query parameters
        response = client.post("/recommend/products", json={})
        assert response.status_code == 400  # Bad request

    @patch("api.routers.ask_review.get_rag_engine")
    def test_ask_question_error_handling(self, mock_get_rag_engine, client):
        """Test error handling in ask question endpoint."""
        # Mock RAG engine to raise exception
        mock_engine = Mock()
        mock_engine.ask_question.side_effect = Exception("Test error")
        mock_get_rag_engine.return_value = mock_engine

        # Test error handling
        response = client.post("/ask_review/ask", json={"question": "Test question"})

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Test error" in data["error"]

    @patch("api.routers.recommend.get_recommender")
    def test_recommend_error_handling(self, mock_get_recommender, client):
        """Test error handling in recommendation endpoint."""
        # Mock recommender to raise exception
        mock_recommender = Mock()
        mock_recommender.get_similar_products.side_effect = Exception("Test error")
        mock_get_recommender.return_value = mock_recommender

        # Test error handling
        response = client.post("/recommend/products", json={"query": "test query"})

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Test error" in data["error"]


class TestAPIValidation:
    """Test cases for API validation."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_question_request_validation(self, client):
        """Test question request validation."""
        # Test valid request
        valid_request = {
            "question": "What do customers say about quality?",
            "max_sources": 5,
        }
        response = client.post("/ask_review/ask", json=valid_request)
        # Should not return validation error (might return 500 due to missing dependencies)
        assert response.status_code in [200, 500]

        # Test invalid request - empty question
        invalid_request = {"question": "", "max_sources": 5}
        response = client.post("/ask_review/ask", json=invalid_request)
        assert response.status_code == 422

        # Test invalid request - question too long
        invalid_request = {
            "question": "x" * 1001,  # Exceeds max_length
            "max_sources": 5,
        }
        response = client.post("/ask_review/ask", json=invalid_request)
        assert response.status_code == 422

    def test_recommendation_request_validation(self, client):
        """Test recommendation request validation."""
        # Test valid request
        valid_request = {
            "query": "wireless headphones",
            "top_k": 10,
            "min_similarity": 0.3,
        }
        response = client.post("/recommend/products", json=valid_request)
        # Should not return validation error (might return 500 due to missing dependencies)
        assert response.status_code in [200, 500]

        # Test invalid request - top_k too high
        invalid_request = {
            "query": "test",
            "top_k": 100,  # Exceeds max value
            "min_similarity": 0.3,
        }
        response = client.post("/recommend/products", json=invalid_request)
        assert response.status_code == 422

        # Test invalid request - min_similarity out of range
        invalid_request = {
            "query": "test",
            "top_k": 10,
            "min_similarity": 1.5,  # Exceeds max value
        }
        response = client.post("/recommend/products", json=invalid_request)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
