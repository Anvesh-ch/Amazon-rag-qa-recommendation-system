# Multi-stage Dockerfile for Amazon Review RAG QA + Recommender system

# Stage 1: Base Python environment
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: API service
FROM base as api

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/processed data/embeddings data/exports

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API
CMD ["python", "api/main.py", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3: Streamlit service
FROM base as streamlit

# Install additional Streamlit dependencies
RUN pip install --no-cache-dir streamlit plotly wordcloud

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/processed data/embeddings data/exports

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Stage 4: Development environment
FROM base as dev

# Install development dependencies
RUN pip install --no-cache-dir \
    jupyter \
    ipykernel \
    pytest \
    pytest-cov \
    flake8 \
    black \
    isort

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/processed data/embeddings data/exports

# Expose ports
EXPOSE 8000 8501 8888

# Default command for development
CMD ["bash"]
