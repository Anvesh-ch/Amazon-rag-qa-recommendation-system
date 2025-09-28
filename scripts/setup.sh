#!/bin/bash

# Amazon Review Intelligence Suite - Setup Script
# This script sets up the environment and runs the complete pipeline

set -e

echo "🛍️ Amazon Review Intelligence Suite - Setup"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Java is installed (required for PySpark)
if ! command -v java &> /dev/null; then
    echo "❌ Java is required for PySpark but not installed."
    echo "Please install Java 8 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/raw data/processed data/exports data/embeddings
mkdir -p logs

# Check if data exists
if [ ! -d "data/raw" ] || [ -z "$(ls -A data/raw)" ]; then
    echo "⚠️  No data found in data/raw/"
    echo "Please place your Amazon review parquet files in data/raw/"
    echo "The system expects data organized in category subdirectories."
    echo ""
    echo "Example structure:"
    echo "data/raw/"
    echo "├── Electronics/"
    echo "│   └── reviews.parquet"
    echo "├── Books/"
    echo "│   └── reviews.parquet"
    echo "└── ..."
    echo ""
    echo "You can download sample data using:"
    echo "python download_all_parquet.py"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run preprocessing: python src/text_preprocess.py"
echo "2. Generate embeddings: python src/embedding.py"
echo "3. Start API: python api/main.py"
echo "4. Start UI: streamlit run streamlit_app/app.py"
echo ""
echo "Or use Docker: docker-compose -f infra/docker-compose.yml up --build"
