"""
FastAPI router for review question answering endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from rag_engine import RAGEngine, RAGEngineManager
from schemas.input_schema import QuestionRequest, QuestionResponse, ErrorResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ask_review", tags=["Review QA"])

# Global RAG engine manager
rag_manager = RAGEngineManager()


def get_rag_engine() -> RAGEngine:
    """Get RAG engine instance."""
    try:
        embeddings_path = "data/embeddings/"
        return rag_manager.get_engine(embeddings_path)
    except Exception as e:
        logger.error(f"Failed to load RAG engine: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to load RAG engine: {str(e)}"
        )


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest, rag_engine: RAGEngine = Depends(get_rag_engine)
) -> QuestionResponse:
    """
    Ask a question about Amazon reviews and get an AI-generated answer with sources.

    Args:
        request: Question request containing the question and optional parameters
        rag_engine: RAG engine instance for processing the question

    Returns:
        QuestionResponse with answer, sources, and metadata
    """
    try:
        logger.info(f"Processing question: {request.question[:100]}...")

        # Ask question using RAG engine
        result = rag_engine.ask_question(
            question=request.question, max_input_chars=3000
        )

        # Limit sources if requested
        if request.max_sources and len(result["sources"]) > request.max_sources:
            result["sources"] = result["sources"][: request.max_sources]
            result["num_sources"] = len(result["sources"])

        # Create response
        response = QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            num_sources=result["num_sources"],
        )

        logger.info(f"Generated answer with {result['num_sources']} sources")
        return response

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )


@router.get("/similar", response_model=Dict[str, Any])
async def get_similar_reviews(
    query: str, top_k: int = 5, rag_engine: RAGEngine = Depends(get_rag_engine)
) -> Dict[str, Any]:
    """
    Get similar reviews for a given query.

    Args:
        query: Text query to find similar reviews
        top_k: Number of similar reviews to return
        rag_engine: RAG engine instance

    Returns:
        Dictionary containing similar reviews and metadata
    """
    try:
        logger.info(f"Finding similar reviews for: {query[:100]}...")

        # Get similar reviews
        similar_reviews = rag_engine.get_similar_reviews(query, top_k=top_k)

        return {
            "query": query,
            "similar_reviews": similar_reviews,
            "num_found": len(similar_reviews),
        }

    except Exception as e:
        logger.error(f"Error finding similar reviews: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error finding similar reviews: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_engine_stats(
    rag_engine: RAGEngine = Depends(get_rag_engine),
) -> Dict[str, Any]:
    """
    Get RAG engine statistics.

    Args:
        rag_engine: RAG engine instance

    Returns:
        Dictionary containing engine statistics
    """
    try:
        stats = rag_engine.get_engine_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting engine stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting engine stats: {str(e)}"
        )
