#!/usr/bin/env python3
"""
PDF Seeding Script for WondrLink

This script processes PDF files from the data directory and seeds the
document chunks into Supabase database. Run this once after setting up
the database, or whenever you add new PDF documents.

Usage:
    python scripts/seed_chunks.py

Environment Variables Required:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key (for bypassing RLS)
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

# Add lib directory to path AFTER importing supabase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Check required environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing required environment variables")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

# Initialize Supabase admin client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Import PDF processing utilities
from pdf_utils import process_pdf


def get_data_directory():
    """Find the data directory with PDF files."""
    # Try multiple locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'data'),
        os.path.join(os.path.dirname(__file__), '..', 'main', 'data'),
        os.path.join(os.path.dirname(__file__), '..', 'public', 'data'),
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            # Check if it has PDF files
            pdfs = [f for f in os.listdir(path) if f.lower().endswith('.pdf')]
            if pdfs:
                return os.path.abspath(path)

    return None


def seed_document(filepath: str) -> dict:
    """
    Process a single PDF and seed its chunks to Supabase.

    Returns:
        dict with 'filename', 'chunks', 'success', 'error'
    """
    filename = os.path.basename(filepath)
    print(f"\nProcessing: {filename}")

    try:
        # Extract and chunk the PDF
        chunks = process_pdf(filepath)

        if not chunks:
            print(f"  WARNING: No text extracted from {filename}")
            return {
                'filename': filename,
                'chunks': 0,
                'success': False,
                'error': 'No text extracted'
            }

        print(f"  Extracted {len(chunks)} chunks")

        # Delete existing chunks for this file
        print(f"  Clearing existing chunks...")
        supabase.table('pdf_chunks').delete().eq('filename', filename).execute()

        # Insert new chunks in batches
        rows = [
            {
                'filename': filename,
                'chunk_index': i,
                'chunk_text': chunk
            }
            for i, chunk in enumerate(chunks)
        ]

        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            supabase.table('pdf_chunks').insert(batch).execute()
            print(f"  Inserted batch {i // batch_size + 1}/{(len(rows) + batch_size - 1) // batch_size}")

        # Update metadata
        supabase.table('document_metadata').upsert({
            'filename': filename,
            'chunk_count': len(chunks),
            'processed_at': datetime.now().isoformat()
        }, on_conflict='filename').execute()

        print(f"  SUCCESS: {len(chunks)} chunks seeded")
        return {
            'filename': filename,
            'chunks': len(chunks),
            'success': True,
            'error': None
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            'filename': filename,
            'chunks': 0,
            'success': False,
            'error': str(e)
        }


def main():
    print("=" * 60)
    print("WondrLink PDF Seeding Script")
    print("=" * 60)

    # Find data directory
    data_dir = get_data_directory()

    if not data_dir:
        print("\nERROR: Could not find data directory with PDF files.")
        print("Expected locations:")
        print("  - ./data/")
        print("  - ./main/data/")
        print("  - ./public/data/")
        sys.exit(1)

    print(f"\nData directory: {data_dir}")

    # Find all PDF files
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("\nNo PDF files found in data directory.")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s)")

    # Process each PDF
    results = []
    for pdf_file in pdf_files:
        filepath = os.path.join(data_dir, pdf_file)
        result = seed_document(filepath)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    total_chunks = sum(r['chunks'] for r in successful)

    print(f"\nTotal documents: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total chunks seeded: {total_chunks}")

    if failed:
        print("\nFailed documents:")
        for r in failed:
            print(f"  - {r['filename']}: {r['error']}")

    print("\nDone!")


if __name__ == '__main__':
    main()
