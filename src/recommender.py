"""
Recommendation system based on content similarity.
Uses FAISS for similarity search and provides rationales from review snippets.
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from collections import defaultdict, Counter
import pandas as pd

logger = logging.getLogger(__name__)


class ProductRecommender:
    """Product recommendation system based on content similarity."""

    def __init__(self, config_path: str = "config.yaml", embeddings_path: str = None):
        """Initialize recommender with configuration."""
        self.config = self._load_config(config_path)
        self.recommend_config = self.config["recommend"]
        self.embedding_config = self.config["embedding"]

        self.embeddings_model = None
        self.index = None
        self.metadata = []
        self.product_embeddings = {}
        self.product_reviews = defaultdict(list)

        # Load embeddings and metadata if path provided
        if embeddings_path:
            self.load_embeddings(embeddings_path)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def load_embeddings(self, embeddings_path: str):
        """Load pre-computed embeddings and metadata."""
        logger.info(f"Loading embeddings from: {embeddings_path}")

        # Load metadata
        metadata_file = os.path.join(embeddings_path, "metadata.pkl")
        with open(metadata_file, "rb") as f:
            self.metadata = pickle.load(f)

        # Load embeddings
        embeddings_file = os.path.join(embeddings_path, "embeddings.npy")
        embeddings = np.load(embeddings_file)

        # Load FAISS index
        index_file = os.path.join(embeddings_path, "faiss_index.bin")
        self.index = faiss.read_index(index_file)

        # Load sentence transformer model
        self.embeddings_model = SentenceTransformer(self.embedding_config["model_name"])

        # Organize data by product
        self._organize_by_product(embeddings)

        logger.info(
            f"Loaded {len(self.metadata)} reviews for {len(self.product_embeddings)} products"
        )

    def _organize_by_product(self, embeddings: np.ndarray):
        """Organize embeddings and metadata by product."""
        for i, (embedding, meta) in enumerate(zip(embeddings, self.metadata)):
            product_id = meta.get("product_id", "")
            if product_id:
                # Store product embedding (average of all reviews for this product)
                if product_id not in self.product_embeddings:
                    self.product_embeddings[product_id] = []
                self.product_embeddings[product_id].append(embedding)

                # Store review metadata
                self.product_reviews[product_id].append(meta)

        # Average embeddings per product
        for product_id in self.product_embeddings:
            self.product_embeddings[product_id] = np.mean(
                self.product_embeddings[product_id], axis=0
            )

    def get_product_embedding(self, product_id: str) -> Optional[np.ndarray]:
        """Get embedding for a specific product."""
        return self.product_embeddings.get(product_id)

    def get_similar_products(
        self, query: str, top_k: int = None, min_similarity: float = None
    ) -> List[Dict[str, Any]]:
        """Get similar products based on query."""
        if self.index is None:
            raise ValueError("FAISS index not loaded. Call load_embeddings first.")

        top_k = top_k or self.recommend_config.get("top_k", 10)
        min_similarity = min_similarity or self.recommend_config.get(
            "min_similarity", 0.3
        )

        # Generate query embedding
        query_embedding = self.embeddings_model.encode([query])

        # Search for similar reviews
        distances, indices = self.index.search(
            query_embedding.astype("float32"), top_k * 3
        )

        # Group by product and calculate similarity scores
        product_scores = defaultdict(list)
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                product_id = meta.get("product_id", "")
                if product_id:
                    # Convert distance to similarity (assuming L2 distance)
                    similarity = 1 / (1 + distance)
                    product_scores[product_id].append(similarity)

        # Calculate average similarity per product
        product_avg_similarities = {}
        for product_id, scores in product_scores.items():
            product_avg_similarities[product_id] = np.mean(scores)

        # Filter by minimum similarity and sort
        filtered_products = {
            pid: sim
            for pid, sim in product_avg_similarities.items()
            if sim >= min_similarity
        }

        sorted_products = sorted(
            filtered_products.items(), key=lambda x: x[1], reverse=True
        )[:top_k]

        # Format results
        results = []
        for product_id, similarity in sorted_products:
            product_info = self._get_product_info(product_id, similarity)
            if product_info:
                results.append(product_info)

        return results

    def _get_product_info(
        self, product_id: str, similarity: float
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive product information."""
        if product_id not in self.product_reviews:
            return None

        reviews = self.product_reviews[product_id]

        # Basic product info
        first_review = reviews[0]
        product_title = first_review.get("product_title", "")
        category = first_review.get("category", "")

        # Calculate statistics
        star_ratings = [
            r.get("star_rating", 0) for r in reviews if r.get("star_rating")
        ]
        avg_rating = np.mean(star_ratings) if star_ratings else 0
        num_reviews = len(reviews)

        # Get representative review snippets
        review_snippets = self._get_review_snippets(reviews)

        # Get rationale (most relevant review snippets)
        rationale = self._generate_rationale(reviews, similarity)

        return {
            "product_id": product_id,
            "product_title": product_title,
            "category": category,
            "similarity_score": similarity,
            "average_rating": round(avg_rating, 2),
            "num_reviews": num_reviews,
            "review_snippets": review_snippets,
            "rationale": rationale,
        }

    def _get_review_snippets(
        self, reviews: List[Dict[str, Any]], max_snippets: int = 3
    ) -> List[str]:
        """Get representative review snippets."""
        # Sort by star rating and text length
        sorted_reviews = sorted(
            reviews,
            key=lambda x: (x.get("star_rating", 0), len(x.get("review_body", ""))),
            reverse=True,
        )

        snippets = []
        for review in sorted_reviews[:max_snippets]:
            review_body = review.get("review_body", "")
            if review_body:
                # Truncate long reviews
                snippet = (
                    review_body[:200] + "..." if len(review_body) > 200 else review_body
                )
                snippets.append(snippet)

        return snippets

    def _generate_rationale(
        self, reviews: List[Dict[str, Any]], similarity: float
    ) -> str:
        """Generate rationale for recommendation."""
        # Get most common positive words
        positive_words = []
        for review in reviews:
            if review.get("star_rating", 0) >= 4:
                review_body = review.get("review_body", "").lower()
                # Simple positive word extraction
                words = review_body.split()
                positive_words.extend([w for w in words if len(w) > 3])

        # Count positive words
        word_counts = Counter(positive_words)
        top_words = [word for word, count in word_counts.most_common(5)]

        # Generate rationale
        rationale_parts = [
            f"Similarity score: {similarity:.3f}",
            f"Based on {len(reviews)} reviews with average rating {np.mean([r.get('star_rating', 0) for r in reviews]):.1f}/5",
        ]

        if top_words:
            rationale_parts.append(f"Key themes: {', '.join(top_words[:3])}")

        return " | ".join(rationale_parts)

    def recommend_by_product(
        self, product_id: str, top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Recommend similar products based on a given product."""
        if product_id not in self.product_embeddings:
            logger.warning(f"Product {product_id} not found in embeddings")
            return []

        # Get product embedding
        product_embedding = self.product_embeddings[product_id]

        # Search for similar products
        distances, indices = self.index.search(
            product_embedding.reshape(1, -1).astype("float32"),
            top_k * 3 if top_k else 50,
        )

        # Filter out the same product and get unique products
        similar_products = []
        seen_products = {product_id}

        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                similar_product_id = meta.get("product_id", "")

                if similar_product_id and similar_product_id not in seen_products:
                    similarity = 1 / (1 + distance)
                    similar_products.append((similar_product_id, similarity))
                    seen_products.add(similar_product_id)

                    if len(similar_products) >= (
                        top_k or self.recommend_config.get("top_k", 10)
                    ):
                        break

        # Format results
        results = []
        for similar_product_id, similarity in similar_products:
            product_info = self._get_product_info(similar_product_id, similarity)
            if product_info:
                results.append(product_info)

        return results

    def get_category_recommendations(
        self, category: str, top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Get top products in a specific category."""
        top_k = top_k or self.recommend_config.get("top_k", 10)

        # Filter products by category
        category_products = []
        for product_id, reviews in self.product_reviews.items():
            if reviews and reviews[0].get("category") == category:
                # Calculate average rating
                ratings = [
                    r.get("star_rating", 0) for r in reviews if r.get("star_rating")
                ]
                if ratings:
                    avg_rating = np.mean(ratings)
                    category_products.append((product_id, avg_rating, len(reviews)))

        # Sort by rating and number of reviews
        category_products.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Format results
        results = []
        for product_id, avg_rating, num_reviews in category_products[:top_k]:
            product_info = self._get_product_info(
                product_id, 0.0
            )  # No similarity for category-based
            if product_info:
                product_info["similarity_score"] = (
                    avg_rating / 5.0
                )  # Normalize rating to similarity
                results.append(product_info)

        return results

    def get_recommendation_stats(self) -> Dict[str, Any]:
        """Get statistics about the recommendation system."""
        stats = {
            "num_products": len(self.product_embeddings),
            "num_reviews": len(self.metadata),
            "categories": list(set(meta.get("category", "") for meta in self.metadata)),
            "avg_reviews_per_product": (
                len(self.metadata) / len(self.product_embeddings)
                if self.product_embeddings
                else 0
            ),
        }
        return stats


def main():
    """Main function for testing recommendation system."""
    import argparse

    parser = argparse.ArgumentParser(description="Test recommendation system")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--embeddings", help="Path to embeddings directory")
    parser.add_argument("--query", help="Query for product search")
    parser.add_argument("--product_id", help="Product ID for similar product search")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize recommender
    embeddings_path = args.embeddings or "data/embeddings/"
    recommender = ProductRecommender(args.config, embeddings_path)

    try:
        print("\n=== Recommendation System Test ===")

        # Test query-based recommendations
        if args.query:
            print(f"\nQuery-based recommendations for: '{args.query}'")
            results = recommender.get_similar_products(args.query, top_k=5)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['product_title']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(
                    f"   Rating: {result['average_rating']}/5 ({result['num_reviews']} reviews)"
                )
                print(f"   Rationale: {result['rationale']}")
                print()

        # Test product-based recommendations
        if args.product_id:
            print(f"\nSimilar products to: {args.product_id}")
            results = recommender.recommend_by_product(args.product_id, top_k=5)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['product_title']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(
                    f"   Rating: {result['average_rating']}/5 ({result['num_reviews']} reviews)"
                )
                print()

        # Print stats
        stats = recommender.get_recommendation_stats()
        print(f"\nSystem Stats:")
        print(f"Products: {stats['num_products']}")
        print(f"Reviews: {stats['num_reviews']}")
        print(f"Categories: {len(stats['categories'])}")

    except Exception as e:
        logger.error(f"Error testing recommendation system: {e}")
        raise


if __name__ == "__main__":
    main()
