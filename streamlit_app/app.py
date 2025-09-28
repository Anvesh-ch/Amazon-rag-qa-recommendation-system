"""
Streamlit frontend for Amazon Review RAG QA + Recommender system.
Single UI with two tabs: Ask Reviews (QA) and Recommendations.
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Amazon Review Intelligence Suite",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_BASE_URL = "http://localhost:8000"
ASK_ENDPOINT = f"{API_BASE_URL}/ask_review"
RECOMMEND_ENDPOINT = f"{API_BASE_URL}/recommend"

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF9900;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #232F3E;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9900;
    }
    .source-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .product-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF9900;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


def check_api_health() -> bool:
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def ask_question(question: str, max_sources: int = 5) -> Optional[Dict[str, Any]]:
    """Ask a question to the RAG engine."""
    try:
        response = requests.post(
            f"{ASK_ENDPOINT}/ask",
            json={"question": question, "max_sources": max_sources},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def get_recommendations(
    query: str = None,
    product_id: str = None,
    category: str = None,
    top_k: int = 10,
    min_similarity: float = 0.3,
) -> Optional[Dict[str, Any]]:
    """Get product recommendations."""
    try:
        params = {"top_k": top_k, "min_similarity": min_similarity}

        if query:
            params["query"] = query
        elif product_id:
            params["product_id"] = product_id
        elif category:
            params["category"] = category

        response = requests.get(
            RECOMMEND_ENDPOINT + "/products", params=params, timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def get_categories() -> Optional[List[str]]:
    """Get available product categories."""
    try:
        response = requests.get(f"{RECOMMEND_ENDPOINT}/categories", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("categories", [])
        return None
    except:
        return None


def display_qa_tab():
    """Display the Question Answering tab."""
    st.markdown(
        '<div class="sub-header">🔍 Ask Questions About Amazon Reviews</div>',
        unsafe_allow_html=True,
    )

    # Question input
    col1, col2 = st.columns([3, 1])

    with col1:
        question = st.text_area(
            "Ask a question about Amazon product reviews:",
            placeholder="e.g., What do customers say about product quality? What are common complaints?",
            height=100,
            key="question_input",
        )

    with col2:
        max_sources = st.slider("Max Sources", 1, 20, 5)
        ask_button = st.button("Ask Question", type="primary", use_container_width=True)

    if ask_button and question:
        with st.spinner("Generating answer..."):
            result = ask_question(question, max_sources)

            if result:
                # Display answer
                st.markdown("### 🤖 AI Answer")
                st.markdown(f"**Question:** {result['question']}")
                st.markdown(f"**Answer:** {result['answer']}")

                # Display sources
                if result["sources"]:
                    st.markdown(f"### 📚 Sources ({result['num_sources']})")

                    for i, source in enumerate(result["sources"], 1):
                        with st.expander(
                            f"Source {i}: {source['metadata'].get('product_title', 'Unknown Product')[:50]}..."
                        ):
                            st.markdown(
                                f"**Product:** {source['metadata'].get('product_title', 'N/A')}"
                            )
                            st.markdown(
                                f"**Category:** {source['metadata'].get('category', 'N/A')}"
                            )
                            st.markdown(
                                f"**Rating:** {source['metadata'].get('star_rating', 'N/A')}/5"
                            )
                            st.markdown(f"**Review:** {source['content']}")

                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sources Found", result["num_sources"])
                with col2:
                    st.metric("Answer Length", len(result["answer"]))
                with col3:
                    st.metric("Processing Time", "~2-5 seconds")


def display_recommendations_tab():
    """Display the Product Recommendations tab."""
    st.markdown(
        '<div class="sub-header">🎯 Product Recommendations</div>',
        unsafe_allow_html=True,
    )

    # Recommendation type selection
    rec_type = st.radio(
        "Choose recommendation type:",
        ["Text Query", "Similar Products", "Category Top"],
        horizontal=True,
    )

    if rec_type == "Text Query":
        query = st.text_input(
            "Describe what you're looking for:",
            placeholder="e.g., wireless headphones with good battery life",
        )
        if st.button("Get Recommendations", type="primary"):
            if query:
                with st.spinner("Finding similar products..."):
                    result = get_recommendations(query=query)
                    if result:
                        display_recommendations(result)
            else:
                st.warning("Please enter a search query.")

    elif rec_type == "Similar Products":
        product_id = st.text_input("Enter Product ID:", placeholder="e.g., B08N5WRWNW")
        if st.button("Find Similar Products", type="primary"):
            if product_id:
                with st.spinner("Finding similar products..."):
                    result = get_recommendations(product_id=product_id)
                    if result:
                        display_recommendations(result)
            else:
                st.warning("Please enter a product ID.")

    elif rec_type == "Category Top":
        categories = get_categories()
        if categories:
            category = st.selectbox("Select Category:", categories)
            if st.button("Get Top Products", type="primary"):
                with st.spinner("Getting top products..."):
                    result = get_recommendations(category=category)
                    if result:
                        display_recommendations(result)
        else:
            st.error("Could not load categories. Please check API connection.")


def display_recommendations(result: Dict[str, Any]):
    """Display recommendation results."""
    recommendations = result.get("recommendations", [])
    query_type = result.get("query_type", "unknown")
    total_found = result.get("total_found", 0)

    st.markdown(f"### Found {total_found} recommendations")

    if not recommendations:
        st.warning("No recommendations found. Try adjusting your search criteria.")
        return

    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        with st.container():
            st.markdown(
                f"""
            <div class="product-card">
                <h4>#{i} {rec['product_title']}</h4>
                <p><strong>Category:</strong> {rec['category']} |
                   <strong>Rating:</strong> {rec['average_rating']}/5 ({rec['num_reviews']} reviews) |
                   <strong>Similarity:</strong> {rec['similarity_score']:.3f}</p>
                <p><strong>Rationale:</strong> {rec['rationale']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Review snippets
            if rec["review_snippets"]:
                with st.expander(
                    f"View Review Snippets ({len(rec['review_snippets'])})"
                ):
                    for j, snippet in enumerate(rec["review_snippets"], 1):
                        st.markdown(f"**Snippet {j}:** {snippet}")

    # Summary statistics
    if len(recommendations) > 1:
        st.markdown("### 📊 Summary Statistics")

        # Create summary data
        df = pd.DataFrame(recommendations)

        col1, col2 = st.columns(2)

        with col1:
            # Average rating distribution
            fig_rating = px.histogram(
                df, x="average_rating", title="Rating Distribution", nbins=10
            )
            fig_rating.update_layout(showlegend=False)
            st.plotly_chart(fig_rating, use_container_width=True)

        with col2:
            # Similarity score distribution
            fig_similarity = px.histogram(
                df,
                x="similarity_score",
                title="Similarity Score Distribution",
                nbins=10,
            )
            fig_similarity.update_layout(showlegend=False)
            st.plotly_chart(fig_similarity, use_container_width=True)


def display_sidebar():
    """Display sidebar with system information."""
    st.sidebar.markdown("## 🛍️ Amazon Review Intelligence Suite")

    # API Status
    if check_api_health():
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.sidebar.markdown(
            "**Note:** Make sure the FastAPI backend is running on port 8000"
        )

    # System Stats
    st.sidebar.markdown("### 📊 System Information")

    try:
        # Get QA stats
        qa_response = requests.get(f"{ASK_ENDPOINT}/stats", timeout=5)
        if qa_response.status_code == 200:
            qa_stats = qa_response.json()
            st.sidebar.metric(
                "Documents Indexed", f"{qa_stats.get('num_documents', 0):,}"
            )
            st.sidebar.metric("Model", qa_stats.get("model_name", "Unknown"))

        # Get recommendation stats
        rec_response = requests.get(f"{RECOMMEND_ENDPOINT}/stats", timeout=5)
        if rec_response.status_code == 200:
            rec_stats = rec_response.json()
            st.sidebar.metric("Products", f"{rec_stats.get('num_products', 0):,}")
            st.sidebar.metric("Reviews", f"{rec_stats.get('num_reviews', 0):,}")
            st.sidebar.metric("Categories", rec_stats.get("num_categories", 0))

    except:
        st.sidebar.info("Stats unavailable")

    # Quick Actions
    st.sidebar.markdown("### ⚡ Quick Actions")

    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()

    if st.sidebar.button("📊 View API Docs"):
        st.sidebar.markdown(f"[Open API Documentation]({API_BASE_URL}/docs)")

    # About
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.markdown(
        """
    This application provides:
    - **Question Answering**: Ask questions about Amazon reviews
    - **Product Recommendations**: Find similar products based on reviews
    - **AI-Powered Insights**: Uses RAG and similarity search
    """
    )


def main():
    """Main application function."""
    # Header
    st.markdown(
        '<div class="main-header">🛍️ Amazon Review Intelligence Suite</div>',
        unsafe_allow_html=True,
    )

    # Sidebar
    display_sidebar()

    # Check API connection
    if not check_api_health():
        st.error(
            """
        **API Connection Error**

        The FastAPI backend is not running. Please:
        1. Start the backend: `python api/main.py`
        2. Ensure it's running on port 8000
        3. Refresh this page
        """
        )
        return

    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Ask Reviews", "🎯 Recommendations"])

    with tab1:
        display_qa_tab()

    with tab2:
        display_recommendations_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Amazon Review Intelligence Suite | Powered by RAG + FAISS + Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
