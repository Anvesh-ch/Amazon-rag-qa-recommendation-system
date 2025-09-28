"""
Pydantic schemas for API input/output validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionRequest(BaseModel):
    """Request schema for asking questions about reviews."""

    question: str = Field(
        ..., description="The question to ask about Amazon reviews", max_length=1000
    )
    max_sources: Optional[int] = Field(
        5, description="Maximum number of sources to return", ge=1, le=20
    )


class QuestionResponse(BaseModel):
    """Response schema for question answering."""

    question: str
    answer: str
    sources: List[Dict[str, Any]]
    num_sources: int
    timestamp: datetime = Field(default_factory=datetime.now)


class RecommendationRequest(BaseModel):
    """Request schema for product recommendations."""

    query: Optional[str] = Field(
        None, description="Text query for finding similar products", max_length=500
    )
    product_id: Optional[str] = Field(
        None, description="Product ID to find similar products to"
    )
    category: Optional[str] = Field(
        None, description="Category to get top products from"
    )
    top_k: Optional[int] = Field(
        10, description="Number of recommendations to return", ge=1, le=50
    )
    min_similarity: Optional[float] = Field(
        0.3, description="Minimum similarity threshold", ge=0.0, le=1.0
    )


class ProductInfo(BaseModel):
    """Schema for product information in recommendations."""

    product_id: str
    product_title: str
    category: str
    similarity_score: float
    average_rating: float
    num_reviews: int
    review_snippets: List[str]
    rationale: str


class RecommendationResponse(BaseModel):
    """Response schema for product recommendations."""

    recommendations: List[ProductInfo]
    query_type: str  # "text_query", "product_similar", "category_top"
    total_found: int
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
