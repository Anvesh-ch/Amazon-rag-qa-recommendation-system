"""
RAG (Retrieval-Augmented Generation) engine for Amazon reviews QA.
Uses FAISS for retrieval and FLAN-T5-base for generation.
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import pickle

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for Amazon reviews question answering."""

    def __init__(self, config_path: str = "config.yaml", embeddings_path: str = None):
        """Initialize RAG engine with configuration."""
        self.config = self._load_config(config_path)
        self.rag_config = self.config["rag"]
        self.embedding_config = self.config["embedding"]

        self.embeddings_model = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.metadata = []

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
        faiss_index = faiss.read_index(index_file)

        # Create LangChain FAISS vectorstore
        self.vectorstore = FAISS.from_embeddings(
            embeddings=embeddings,
            embedding=HuggingFaceEmbeddings(
                model_name=self.embedding_config["model_name"]
            ),
            metadatas=self.metadata,
        )

        # Replace the FAISS index with our loaded one
        self.vectorstore.index = faiss_index

        logger.info(f"Loaded {len(self.metadata)} documents into vectorstore")

    def load_llm(self):
        """Load the FLAN-T5 language model."""
        model_name = self.rag_config["generator_model"]
        logger.info(f"Loading language model: {model_name}")

        # Load tokenizer and model
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )

        # Create HuggingFace pipeline
        from transformers import pipeline

        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            device=0 if torch.cuda.is_available() else -1,
        )

        self.llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("Language model loaded successfully")

    def create_qa_chain(self):
        """Create the QA chain with custom prompt."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not loaded. Call load_embeddings first.")

        if self.llm is None:
            self.load_llm()

        # Custom prompt template
        prompt_template = """Use the following pieces of Amazon product reviews to answer the question.
        If you don't know the answer based on the provided context, just say that you don't know, don't try to make up an answer.

        Context:
        {context}

        Question: {question}

        Answer: Based on the Amazon reviews, """

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.rag_config.get("top_k", 5)}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
        )

        logger.info("QA chain created successfully")

    def ask_question(
        self, question: str, max_input_chars: int = None
    ) -> Dict[str, Any]:
        """Ask a question and get an answer with sources."""
        if self.qa_chain is None:
            self.create_qa_chain()

        max_chars = max_input_chars or self.rag_config.get("max_input_chars", 3000)

        # Truncate question if too long
        if len(question) > max_chars:
            question = question[:max_chars]
            logger.warning(f"Question truncated to {max_chars} characters")

        logger.info(f"Processing question: {question[:100]}...")

        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})

            # Extract answer and sources
            answer = result.get("result", "No answer generated")
            source_docs = result.get("source_documents", [])

            # Format sources with metadata
            sources = []
            for doc in source_docs:
                source_info = {
                    "content": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    "metadata": doc.metadata,
                }
                sources.append(source_info)

            response = {
                "question": question,
                "answer": answer,
                "sources": sources,
                "num_sources": len(sources),
            }

            logger.info(f"Generated answer with {len(sources)} sources")
            return response

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "num_sources": 0,
            }

    def get_similar_reviews(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get similar reviews for a query."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not loaded. Call load_embeddings first.")

        # Get similar documents
        docs = self.vectorstore.similarity_search(query, k=top_k)

        # Format results
        results = []
        for doc in docs:
            result = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": getattr(doc, "score", None),
            }
            results.append(result)

        return results

    def batch_ask_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Ask multiple questions in batch."""
        results = []
        for question in questions:
            result = self.ask_question(question)
            results.append(result)
        return results

    def get_engine_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG engine."""
        stats = {
            "num_documents": len(self.metadata) if self.metadata else 0,
            "model_name": self.rag_config["generator_model"],
            "embedding_model": self.embedding_config["model_name"],
            "top_k": self.rag_config.get("top_k", 5),
            "max_input_chars": self.rag_config.get("max_input_chars", 3000),
        }
        return stats


class RAGEngineManager:
    """Manager class for RAG engine instances."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize RAG engine manager."""
        self.config_path = config_path
        self.engines = {}

    def get_engine(self, embeddings_path: str) -> RAGEngine:
        """Get or create a RAG engine for the given embeddings path."""
        if embeddings_path not in self.engines:
            self.engines[embeddings_path] = RAGEngine(self.config_path, embeddings_path)
        return self.engines[embeddings_path]

    def clear_engines(self):
        """Clear all engine instances."""
        self.engines.clear()


def main():
    """Main function for testing RAG engine."""
    import argparse

    parser = argparse.ArgumentParser(description="Test RAG engine")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--embeddings", help="Path to embeddings directory")
    parser.add_argument("--question", help="Question to ask")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize RAG engine
    embeddings_path = args.embeddings or "data/embeddings/"
    engine = RAGEngine(args.config, embeddings_path)

    try:
        # Test question
        question = (
            args.question or "What are customers saying about the product quality?"
        )

        # Ask question
        result = engine.ask_question(question)

        print("\n=== RAG Engine Test ===")
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        print(f"Number of sources: {result['num_sources']}")

        if result["sources"]:
            print("\nSources:")
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. {source['content'][:100]}...")
                print(f"   Metadata: {source['metadata']}")

    except Exception as e:
        logger.error(f"Error testing RAG engine: {e}")
        raise


if __name__ == "__main__":
    main()
