"""
FastAPI main application for Amazon Review RAG QA + Recommender system.
"""

import logging
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from routers.ask_review import router as ask_review_router
from routers.recommend import router as recommend_router
from schemas.input_schema import HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Amazon Review RAG QA + Recommender API",
    description="API for question answering and product recommendations based on Amazon reviews",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ask_review_router)
app.include_router(recommend_router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic health check."""
    return HealthResponse(
        status="healthy", message="Amazon Review RAG QA + Recommender API is running"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="All systems operational")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail, detail=f"HTTP {exc.status_code} error"
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error="Internal server error", detail=str(exc)).dict(),
    )


def main():
    """Main function to run the FastAPI server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Amazon Review RAG QA + Recommender API"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    logger.info(f"Starting API server on {args.host}:{args.port}")

    uvicorn.run(
        "main:app", host=args.host, port=args.port, reload=args.reload, log_level="info"
    )


if __name__ == "__main__":
    main()
