#!/bin/bash

# Amazon Review Intelligence Suite - Pipeline Runner
# This script runs the complete data processing pipeline

set -e

echo "🛍️ Amazon Review Intelligence Suite - Pipeline Runner"
echo "====================================================="

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if data exists
if [ ! -d "data/raw" ] || [ -z "$(ls -A data/raw)" ]; then
    echo "❌ No data found in data/raw/"
    echo "Please run setup.sh first or place your data in data/raw/"
    exit 1
fi

# Step 1: Preprocessing
echo "📊 Step 1: Running preprocessing pipeline..."
python src/text_preprocess.py --input "data/raw/*/*.parquet"

if [ $? -eq 0 ]; then
    echo "✅ Preprocessing completed successfully"
else
    echo "❌ Preprocessing failed"
    exit 1
fi

# Step 2: Generate embeddings
echo "🧠 Step 2: Generating embeddings and building FAISS index..."
python src/embedding.py --input "data/processed/reviews_clean.parquet"

if [ $? -eq 0 ]; then
    echo "✅ Embedding generation completed successfully"
else
    echo "❌ Embedding generation failed"
    exit 1
fi

# Step 3: Test the systems
echo "🧪 Step 3: Testing the systems..."
python -c "
import sys
sys.path.append('src')
from rag_engine import RAGEngine
from recommender import ProductRecommender

print('Testing RAG engine...')
rag = RAGEngine(embeddings_path='data/embeddings/')
print('✅ RAG engine loaded successfully')

print('Testing recommender...')
rec = ProductRecommender(embeddings_path='data/embeddings/')
print('✅ Recommender loaded successfully')
"

if [ $? -eq 0 ]; then
    echo "✅ System tests passed"
else
    echo "❌ System tests failed"
    exit 1
fi

echo ""
echo "🎉 Pipeline completed successfully!"
echo ""
echo "📊 Generated files:"
echo "- data/processed/reviews_clean.parquet (processed data)"
echo "- data/exports/eda_sample.parquet (EDA sample)"
echo "- data/embeddings/ (embeddings and FAISS index)"
echo ""
echo "🚀 Ready to start the services:"
echo "1. Start API: python api/main.py"
echo "2. Start UI: streamlit run streamlit_app/app.py"
echo "3. Or use Docker: docker-compose -f infra/docker-compose.yml up"
