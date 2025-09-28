"""
FastAPI router for product recommendation endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from recommender import ProductRecommender
from schemas.input_schema import (
    RecommendationRequest,
    RecommendationResponse,
    ProductInfo,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/recommend", tags=["Product Recommendations"])

# Global recommender instance
recommender = None


def get_recommender() -> ProductRecommender:
    """Get recommender instance."""
    global recommender
    if recommender is None:
        try:
            embeddings_path = "data/embeddings/"
            recommender = ProductRecommender(embeddings_path=embeddings_path)
        except Exception as e:
            logger.error(f"Failed to load recommender: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to load recommender: {str(e)}"
            )
    return recommender


@router.post("/products", response_model=RecommendationResponse)
async def recommend_products(
    request: RecommendationRequest,
    recommender: ProductRecommender = Depends(get_recommender),
) -> RecommendationResponse:
    """
    Get product recommendations based on query, product ID, or category.

    Args:
        request: Recommendation request with query, product_id, or category
        recommender: Product recommender instance

    Returns:
        RecommendationResponse with recommended products and metadata
    """
    try:
        recommendations = []
        query_type = "unknown"

        # Determine recommendation type and get results
        if request.query:
            logger.info(f"Getting recommendations for query: {request.query[:100]}...")
            recommendations = recommender.get_similar_products(
                query=request.query,
                top_k=request.top_k,
                min_similarity=request.min_similarity,
            )
            query_type = "text_query"

        elif request.product_id:
            logger.info(f"Getting similar products to: {request.product_id}")
            recommendations = recommender.recommend_by_product(
                product_id=request.product_id, top_k=request.top_k
            )
            query_type = "product_similar"

        elif request.category:
            logger.info(f"Getting top products in category: {request.category}")
            recommendations = recommender.get_category_recommendations(
                category=request.category, top_k=request.top_k
            )
            query_type = "category_top"

        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either query, product_id, or category",
            )

        # Convert to ProductInfo objects
        product_infos = []
        for rec in recommendations:
            product_info = ProductInfo(
                product_id=rec["product_id"],
                product_title=rec["product_title"],
                category=rec["category"],
                similarity_score=rec["similarity_score"],
                average_rating=rec["average_rating"],
                num_reviews=rec["num_reviews"],
                review_snippets=rec["review_snippets"],
                rationale=rec["rationale"],
            )
            product_infos.append(product_info)

        # Create response
        response = RecommendationResponse(
            recommendations=product_infos,
            query_type=query_type,
            total_found=len(product_infos),
        )

        logger.info(f"Returned {len(product_infos)} recommendations")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/products", response_model=RecommendationResponse)
async def recommend_products_get(
    query: Optional[str] = Query(
        None, description="Text query for finding similar products"
    ),
    product_id: Optional[str] = Query(
        None, description="Product ID to find similar products to"
    ),
    category: Optional[str] = Query(
        None, description="Category to get top products from"
    ),
    top_k: int = Query(
        10, description="Number of recommendations to return", ge=1, le=50
    ),
    min_similarity: float = Query(
        0.3, description="Minimum similarity threshold", ge=0.0, le=1.0
    ),
    recommender: ProductRecommender = Depends(get_recommender),
) -> RecommendationResponse:
    """
    Get product recommendations via GET request.

    Args:
        query: Text query for finding similar products
        product_id: Product ID to find similar products to
        category: Category to get top products from
        top_k: Number of recommendations to return
        min_similarity: Minimum similarity threshold
        recommender: Product recommender instance

    Returns:
        RecommendationResponse with recommended products and metadata
    """
    # Create request object
    request = RecommendationRequest(
        query=query,
        product_id=product_id,
        category=category,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    # Use the POST endpoint logic
    return await recommend_products(request, recommender)


@router.get("/categories", response_model=Dict[str, Any])
async def get_categories(
    recommender: ProductRecommender = Depends(get_recommender),
) -> Dict[str, Any]:
    """
    Get available product categories.

    Args:
        recommender: Product recommender instance

    Returns:
        Dictionary containing available categories
    """
    try:
        stats = recommender.get_recommendation_stats()
        return {
            "categories": stats["categories"],
            "total_categories": len(stats["categories"]),
        }

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting categories: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_recommender_stats(
    recommender: ProductRecommender = Depends(get_recommender),
) -> Dict[str, Any]:
    """
    Get recommender system statistics.

    Args:
        recommender: Product recommender instance

    Returns:
        Dictionary containing recommender statistics
    """
    try:
        stats = recommender.get_recommendation_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting recommender stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting recommender stats: {str(e)}"
        )
