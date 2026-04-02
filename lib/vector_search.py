"""
Vector search module for WondrLink hybrid RAG.

Uses Together AI's intfloat/multilingual-e5-large-instruct for query embeddings
and Supabase pgvector for similarity search via the match_chunks() RPC function.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Lazy-initialized Together client
_together_client = None
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"


def _get_together_client():
    """Lazy initialize Together client."""
    global _together_client
    if _together_client is None:
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            logger.warning("TOGETHER_API_KEY not set — vector search unavailable")
            return None
        from together import Together
        _together_client = Together(api_key=api_key)
    return _together_client


def embed_query(text: str) -> Optional[List[float]]:
    """
    Generate embedding for a query string.

    Args:
        text: The query text to embed

    Returns:
        List of 1024 floats, or None if embedding fails
    """
    client = _get_together_client()
    if client is None:
        return None

    try:
        # Truncate to ~450 tokens (1800 chars) for the 512-token context window
        safe_text = text[:1800] if len(text) > 1800 else text
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=safe_text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return None


def vector_search(query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search against pdf_chunks.

    Uses the match_chunks() RPC function in Supabase which runs
    cosine similarity against the HNSW index.

    Args:
        query: The user's query text
        top_k: Number of results to return
        threshold: Minimum similarity score (0-1)

    Returns:
        List of dicts with 'content', 'document_id', 'chunk_index', 'similarity'
        Returns empty list if vector search is unavailable
    """
    query_embedding = embed_query(query)
    if query_embedding is None:
        logger.info("Vector search skipped — no embedding available")
        return []

    try:
        from supabase_client import get_supabase_client
        client = get_supabase_client()

        result = client.rpc('match_chunks', {
            'query_embedding': query_embedding,
            'match_count': top_k,
            'match_threshold': threshold
        }).execute()

        if result.data:
            logger.info(f"Vector search returned {len(result.data)} results")
            return result.data
        return []

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []
