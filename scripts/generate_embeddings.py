#!/usr/bin/env python3
"""
Generate vector embeddings for all PDF chunks in Supabase.

Uses Together AI's intfloat/multilingual-e5-large-instruct model (1024 dimensions).
Free on Together AI's serverless API.

Usage:
    python scripts/generate_embeddings.py

Environment Variables Required:
    TOGETHER_API_KEY - Together AI API key
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key
"""

import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

from together import Together
from supabase import create_client

# Check required env vars
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not TOGETHER_API_KEY:
    print("ERROR: Missing TOGETHER_API_KEY")
    sys.exit(1)
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

# Initialize clients
together_client = Together(api_key=TOGETHER_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
EMBEDDING_DIMS = 1024
BATCH_SIZE = 10  # Small batches to isolate failures


def get_chunks_without_embeddings():
    """Fetch all chunks that don't have embeddings yet."""
    all_chunks = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table('pdf_chunks') \
            .select('id, content') \
            .is_('embedding', 'null') \
            .order('id') \
            .range(offset, offset + page_size - 1) \
            .execute()

        if not result.data:
            break

        all_chunks.extend(result.data)
        offset += page_size

        if len(result.data) < page_size:
            break

    return all_chunks


def truncate_for_embedding(text: str, max_chars: int = 1400) -> str:
    """Truncate text to fit within the model's 512 token context window.
    ~1400 chars ≈ 350 tokens, safely under the 512 limit.
    Medical text tokenizes longer than normal text due to terminology."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.7:
        return truncated[:last_period + 1]
    return truncated


def generate_embeddings_batch(texts: list) -> list:
    """Generate embeddings for a batch of texts using Together AI."""
    # Truncate texts to fit model's 512 token context window
    safe_texts = [truncate_for_embedding(t) for t in texts]
    response = together_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=safe_texts
    )
    return [item.embedding for item in response.data]


def update_chunk_embedding(chunk_id: str, embedding: list):
    """Update a single chunk's embedding in Supabase."""
    supabase.table('pdf_chunks') \
        .update({'embedding': embedding}) \
        .eq('id', chunk_id) \
        .execute()


def main():
    print("=" * 60)
    print("WondrLink Embedding Generation")
    print(f"Model: {EMBEDDING_MODEL} ({EMBEDDING_DIMS} dimensions)")
    print("Provider: Together AI (free serverless)")
    print("=" * 60)

    # Get chunks needing embeddings
    print("\n1. Fetching chunks without embeddings...")
    chunks = get_chunks_without_embeddings()
    print(f"   Found {len(chunks)} chunks to embed")

    if not chunks:
        print("   All chunks already have embeddings. Done!")
        return

    # Process in batches
    print(f"\n2. Generating embeddings in batches of {BATCH_SIZE}...")
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    processed = 0
    errors = 0

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        try:
            texts = [c['content'] for c in batch]
            embeddings = generate_embeddings_batch(texts)

            for chunk, embedding in zip(batch, embeddings):
                try:
                    update_chunk_embedding(chunk['id'], embedding)
                    processed += 1
                except Exception as e:
                    print(f"   ERROR updating chunk {chunk['id']}: {e}")
                    errors += 1

            print(f"   Batch {batch_num}/{total_batches}: {len(batch)} chunks embedded ({processed} total)")

            # Rate limiting
            if batch_num < total_batches:
                time.sleep(1)

        except Exception as e:
            # Batch failed — try each chunk individually with aggressive truncation
            print(f"   Batch {batch_num} failed, retrying individually...")
            for chunk in batch:
                try:
                    text = truncate_for_embedding(chunk['content'], max_chars=1000)
                    emb = generate_embeddings_batch([text])
                    update_chunk_embedding(chunk['id'], emb[0])
                    processed += 1
                except Exception as e2:
                    # Last resort: truncate to 500 chars
                    try:
                        text = chunk['content'][:500]
                        emb = generate_embeddings_batch([text])
                        update_chunk_embedding(chunk['id'], emb[0])
                        processed += 1
                    except Exception as e3:
                        errors += 1
            print(f"   Batch {batch_num} individual retry done ({processed} total)")
            time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total chunks: {len(chunks)}")
    print(f"Successfully embedded: {processed}")
    print(f"Errors: {errors}")

    # Verify
    print("\n3. Verifying...")
    result = supabase.table('pdf_chunks') \
        .select('id', count='exact') \
        .not_.is_('embedding', 'null') \
        .execute()
    print(f"   Chunks with embeddings: {result.count}")

    result_null = supabase.table('pdf_chunks') \
        .select('id', count='exact') \
        .is_('embedding', 'null') \
        .execute()
    print(f"   Chunks without embeddings: {result_null.count}")

    print("\nDone!")


if __name__ == '__main__':
    main()
