"""
Embedding generation and FAISS index building module.
Uses sentence-transformers for generating embeddings and FAISS for indexing.
"""

import os
import pickle
import yaml
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm
import torch

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings and build FAISS index for Amazon reviews."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize embedding generator with configuration."""
        self.config = self._load_config(config_path)
        self.embedding_config = self.config["embedding"]
        self.model = None
        self.index = None
        self.metadata = []

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def load_model(self):
        """Load the sentence transformer model."""
        model_name = self.embedding_config["model_name"]
        logger.info(f"Loading model: {model_name}")

        self.model = SentenceTransformer(model_name)

        # Set device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(device)
        logger.info(f"Model loaded on device: {device}")

    def generate_embeddings(
        self, texts: List[str], batch_size: int = None
    ) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if self.model is None:
            self.load_model()

        batch_size = batch_size or self.embedding_config.get("batch_size", 64)
        normalize = self.embedding_config.get("normalize", True)

        logger.info(
            f"Generating embeddings for {len(texts)} texts with batch size {batch_size}"
        )

        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
        )

        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings

    def build_faiss_index(
        self, embeddings: np.ndarray, index_type: str = "HNSW"
    ) -> faiss.Index:
        """Build FAISS index from embeddings."""
        logger.info(f"Building FAISS index of type: {index_type}")

        dimension = embeddings.shape[1]

        if index_type == "HNSW":
            # Hierarchical Navigable Small World index
            index = faiss.IndexHNSWFlat(dimension, 32)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 50
        elif index_type == "IVF":
            # Inverted File index
            nlist = min(100, len(embeddings) // 100)  # Number of clusters
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            index.train(embeddings)
        else:
            # Default to flat index
            index = faiss.IndexFlatL2(dimension)

        # Add embeddings to index
        index.add(embeddings.astype("float32"))

        logger.info(f"FAISS index built with {index.ntotal} vectors")
        return index

    def search_similar(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar embeddings in the index."""
        if self.index is None:
            raise ValueError("FAISS index not built. Call build_faiss_index first.")

        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)

        return distances[0], indices[0]

    def process_reviews_data(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Process reviews dataframe and generate embeddings."""
        logger.info(f"Processing {len(df)} reviews")

        # Prepare texts for embedding
        texts = df["combined_text"].tolist()

        # Generate embeddings
        embeddings = self.generate_embeddings(texts)

        # Prepare metadata
        metadata = []
        for idx, row in df.iterrows():
            metadata.append(
                {
                    "review_id": row.get("review_id", ""),
                    "product_id": row.get("product_id", ""),
                    "product_title": row.get("product_title", ""),
                    "review_body": row.get("review_body", ""),
                    "star_rating": row.get("star_rating", 0),
                    "category": row.get("category", ""),
                    "combined_text": row.get("combined_text", ""),
                    "text_length": row.get("text_length", 0),
                    "token_count": row.get("token_count", 0),
                }
            )

        return embeddings, metadata

    def save_embeddings_and_index(
        self, embeddings: np.ndarray, metadata: List[Dict[str, Any]], output_path: str
    ):
        """Save embeddings, index, and metadata."""
        logger.info(f"Saving embeddings and index to: {output_path}")

        # Create output directory
        os.makedirs(output_path, exist_ok=True)

        # Save embeddings
        embeddings_file = os.path.join(output_path, "embeddings.npy")
        np.save(embeddings_file, embeddings)
        logger.info(f"Saved embeddings to: {embeddings_file}")

        # Save metadata
        metadata_file = os.path.join(output_path, "metadata.pkl")
        with open(metadata_file, "wb") as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved metadata to: {metadata_file}")

        # Save index
        index_file = os.path.join(output_path, "faiss_index.bin")
        faiss.write_index(self.index, index_file)
        logger.info(f"Saved FAISS index to: {index_file}")

        # Save model info
        model_info = {
            "model_name": self.embedding_config["model_name"],
            "embedding_dimension": embeddings.shape[1],
            "num_embeddings": len(embeddings),
            "index_type": self.embedding_config.get("index_type", "HNSW"),
            "normalize": self.embedding_config.get("normalize", True),
        }

        model_info_file = os.path.join(output_path, "model_info.yaml")
        with open(model_info_file, "w") as f:
            yaml.dump(model_info, f)
        logger.info(f"Saved model info to: {model_info_file}")

    def load_embeddings_and_index(self, input_path: str):
        """Load embeddings, index, and metadata."""
        logger.info(f"Loading embeddings and index from: {input_path}")

        # Load model
        self.load_model()

        # Load embeddings
        embeddings_file = os.path.join(input_path, "embeddings.npy")
        embeddings = np.load(embeddings_file)
        logger.info(f"Loaded embeddings shape: {embeddings.shape}")

        # Load metadata
        metadata_file = os.path.join(input_path, "metadata.pkl")
        with open(metadata_file, "rb") as f:
            metadata = pickle.load(f)
        logger.info(f"Loaded {len(metadata)} metadata records")

        # Load index
        index_file = os.path.join(input_path, "faiss_index.bin")
        self.index = faiss.read_index(index_file)
        logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")

        # Load model info
        model_info_file = os.path.join(input_path, "model_info.yaml")
        with open(model_info_file, "r") as f:
            model_info = yaml.safe_load(f)
        logger.info(f"Model info: {model_info}")

        return embeddings, metadata

    def build_from_processed_data(self, processed_parquet_path: str):
        """Build embeddings and index from processed parquet data."""
        logger.info(
            f"Building embeddings from processed data: {processed_parquet_path}"
        )

        # Load processed data
        df = pd.read_parquet(processed_parquet_path)
        logger.info(f"Loaded {len(df)} processed reviews")

        # Process and generate embeddings
        embeddings, metadata = self.process_reviews_data(df)

        # Build FAISS index
        index_type = self.embedding_config.get("index_type", "HNSW")
        self.index = self.build_faiss_index(embeddings, index_type)

        # Save everything
        output_path = self.embedding_config["output_path"]
        self.save_embeddings_and_index(embeddings, metadata, output_path)

        logger.info("Embedding generation and indexing completed")
        return embeddings, metadata


def main():
    """Main function for running embedding generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate embeddings and build FAISS index"
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--input", help="Path to processed parquet file")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize embedding generator
    generator = EmbeddingGenerator(args.config)

    try:
        # Get input path from args or config
        input_path = args.input or generator.config["preprocess"]["output_parquet"]

        # Build embeddings and index
        embeddings, metadata = generator.build_from_processed_data(input_path)

        print("\n=== Embedding Generation Statistics ===")
        print(f"Number of embeddings: {len(embeddings):,}")
        print(f"Embedding dimension: {embeddings.shape[1]}")
        print(f"Index type: {generator.embedding_config.get('index_type', 'HNSW')}")
        print(f"Output path: {generator.embedding_config['output_path']}")

    except Exception as e:
        logger.error(f"Error in embedding generation: {e}")
        raise


if __name__ == "__main__":
    main()
