# supabase_storage.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase_client import get_supabase_client, get_admin_client

logger = logging.getLogger("supabase_storage")


# -------------------------
# Patient Profile Operations
# Uses patient_profiles table with raw_profile JSON column
# -------------------------

def save_profile(user_id: str, profile_data: dict) -> bool:
    """
    Save or update a patient profile for a user.

    Args:
        user_id: The user's UUID
        profile_data: The patient profile JSON data

    Returns:
        True if successful, False otherwise
    """
    try:
        # Use admin client to bypass RLS - user_id is verified in API layer
        client = get_admin_client()

        # Extract key fields from profile_data for individual columns
        patient = profile_data.get('patient', {})
        diagnosis = profile_data.get('primaryDiagnosis', {})

        profile_row = {
            'user_id': user_id,
            'raw_profile': profile_data,
            'patient_name': patient.get('name'),
            'date_of_birth': patient.get('dob'),
            'gender': patient.get('sex'),
            'ecog_score': patient.get('ecog'),
            'allergies': patient.get('allergies'),
            'comorbidities': patient.get('comorbidities'),
            'cancer_type': diagnosis.get('site'),
            'histology': diagnosis.get('histology'),
            'cancer_stage': diagnosis.get('stage'),
            'biomarkers': diagnosis.get('biomarkers', {}),
            'current_treatments': profile_data.get('treatments', []),
            'updated_at': datetime.now().isoformat()
        }

        client.table('patient_profiles').upsert(
            profile_row,
            on_conflict='user_id'
        ).execute()

        logger.info(f"Saved patient profile for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save profile: {e}")
        return False


def load_profile(user_id: str) -> dict:
    """
    Load a patient profile for a user.

    Args:
        user_id: The user's UUID

    Returns:
        Profile data dict (from raw_profile), or empty dict if not found
    """
    try:
        # Use admin client to bypass RLS - user_id is verified in API layer
        client = get_admin_client()
        result = client.table('patient_profiles') \
            .select('raw_profile') \
            .eq('user_id', user_id) \
            .single() \
            .execute()

        if result.data:
            logger.info(f"Loaded patient profile for user {user_id}")
            return result.data.get('raw_profile', {})
        return {}
    except Exception as e:
        # Single() throws if no rows found, which is expected
        if "0 rows" not in str(e).lower():
            logger.error(f"Failed to load profile: {e}")
        return {}


def clear_profile(user_id: str) -> bool:
    """
    Delete a patient profile for a user.

    Args:
        user_id: The user's UUID

    Returns:
        True if successful, False otherwise
    """
    try:
        # Use admin client to bypass RLS - user_id is verified in API layer
        client = get_admin_client()
        client.table('patient_profiles') \
            .delete() \
            .eq('user_id', user_id) \
            .execute()

        logger.info(f"Cleared patient profile for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear profile: {e}")
        return False


def merge_profile_updates(target: dict, updates: dict) -> dict:
    """Recursively merge updates into target profile."""
    for key, value in updates.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            merge_profile_updates(target[key], value)
        else:
            target[key] = value
    return target


def update_profile_with_sources(user_id: str, updates: dict, source_info: dict) -> bool:
    """
    Update patient profile with new data and track sources.
    
    source_info should look like: {"source_type": "chat", "session_id": "...", "timestamp": "..."}
    """
    if not updates:
        return True

    try:
        current_profile = load_profile(user_id)
        
        # Merge updates into current profile
        updated_profile = merge_profile_updates(current_profile, updates)
        
        # Handle field-specific sources
        # We'll store sources in a special '_sources' field within the profile
        if '_sources' not in updated_profile:
            updated_profile['_sources'] = {}
        
        def track_sources(data, path=""):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    track_sources(value, current_path)
                else:
                    updated_profile['_sources'][current_path] = source_info

        track_sources(updates)
        
        # Save the updated profile back
        return save_profile(user_id, updated_profile)
    except Exception as e:
        logger.error(f"Failed to update profile with sources: {e}")
        return False


# -------------------------
# Document Chunk Operations
# -------------------------

def save_document_chunks(filename: str, chunks: List[str]) -> bool:
    """
    Save document chunks to the database.
    Uses admin client to bypass RLS since chunks are shared.

    Args:
        filename: The source document filename
        chunks: List of text chunks

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_admin_client()

        # Delete existing chunks for this file
        client.table('pdf_chunks') \
            .delete() \
            .eq('filename', filename) \
            .execute()

        if not chunks:
            logger.info(f"No chunks to save for {filename}")
            return True

        # Insert new chunks in batches
        rows = [
            {
                'filename': filename,
                'chunk_index': i,
                'chunk_text': chunk
            }
            for i, chunk in enumerate(chunks)
        ]

        # Batch insert (Supabase has row limits)
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            client.table('pdf_chunks').insert(batch).execute()

        # Update metadata
        client.table('document_metadata').upsert({
            'filename': filename,
            'chunk_count': len(chunks),
            'processed_at': datetime.now().isoformat()
        }, on_conflict='filename').execute()

        logger.info(f"Saved {len(chunks)} chunks for {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save document chunks: {e}")
        return False


def load_all_chunks() -> List[Dict[str, Any]]:
    """
    Load all document chunks from the database with metadata.

    Returns:
        List of dicts: [{'content': str, 'filename': str, 'chunk_index': int, ...}]
    """
    try:
        client = get_supabase_client()

        # Get total count first
        count_result = client.table('pdf_chunks') \
            .select('id', count='exact') \
            .execute()

        total_count = count_result.count or 0

        if total_count == 0:
            logger.info("No chunks found in database")
            return []

        # Fetch all chunks (paginated if necessary)
        all_chunks = []
        page_size = 1000
        offset = 0

        while offset < total_count:
            # Select relevant columns. Assuming 'content' keeps the text.
            # If 'chunk_text' was used for insert and 'content' for select, we try both or stick to 'content' if that's what works.
            # We'll try to select filename too.
            result = client.table('pdf_chunks') \
                .select('content, filename, chunk_index, chunk_text') \
                .order('document_id') \
                .order('chunk_index') \
                .range(offset, offset + page_size - 1) \
                .execute()

            if result.data:
                # normalize content
                for row in result.data:
                    # Prefer content, fallback to chunk_text
                    text = row.get('content') or row.get('chunk_text') or ""
                    row['content'] = text
                    all_chunks.append(row)

            offset += page_size

        logger.info(f"Loaded {len(all_chunks)} chunks from database")
        return all_chunks
    except Exception as e:
        logger.error(f"Failed to load chunks: {e}")
        return []


def get_document_metadata() -> List[Dict[str, Any]]:
    """
    Get metadata for all processed documents.

    Returns:
        List of document metadata dicts
    """
    try:
        client = get_supabase_client()
        result = client.table('pdf_documents') \
            .select('id, filename, chunk_count, processed_at, status') \
            .order('filename') \
            .execute()

        return result.data or []
    except Exception as e:
        logger.error(f"Failed to get document metadata: {e}")
        return []


def remove_document(filename: str) -> bool:
    """
    Remove a document and its chunks from the database.

    Args:
        filename: The document filename to remove

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_admin_client()

        # Get document ID first
        doc_result = client.table('pdf_documents') \
            .select('id') \
            .eq('filename', filename) \
            .single() \
            .execute()

        if not doc_result.data:
            logger.warning(f"Document {filename} not found")
            return False

        doc_id = doc_result.data['id']

        # Delete chunks by document_id
        client.table('pdf_chunks') \
            .delete() \
            .eq('document_id', doc_id) \
            .execute()

        # Delete document metadata
        client.table('pdf_documents') \
            .delete() \
            .eq('id', doc_id) \
            .execute()

        logger.info(f"Removed document {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to remove document: {e}")
        return False


# -------------------------
# Conversation History Operations
# Uses: conversations (sessions) and messages (individual Q&A)
# -------------------------

def get_or_create_conversation(session_id: str, user_id: str) -> Optional[str]:
    """
    Get or create a conversation for a session.

    Returns:
        The conversation UUID, or None on error
    """
    try:
        client = get_supabase_client()

        # Try to find existing conversation
        result = client.table('conversations') \
            .select('id') \
            .eq('session_id', session_id) \
            .eq('user_id', user_id) \
            .limit(1) \
            .execute()

        if result.data:
            return result.data[0]['id']

        # Create new conversation
        new_result = client.table('conversations').insert({
            'session_id': session_id,
            'user_id': user_id,
            'title': 'Chat Session',
            'is_active': True
        }).execute()

        if new_result.data:
            return new_result.data[0]['id']

        return None
    except Exception as e:
        logger.error(f"Failed to get/create conversation: {e}")
        return None


def add_conversation(session_id: str, user_id: str, question: str, answer: str,
                     metadata: dict = None) -> bool:
    """
    Add a conversation entry (question + answer as two messages).

    Args:
        session_id: The chat session ID
        user_id: The user's UUID
        question: The user's question
        answer: The AI's response
        metadata: Optional additional metadata

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_supabase_client()

        # Get or create conversation
        conversation_id = get_or_create_conversation(session_id, user_id)
        if not conversation_id:
            return False

        # Get next sequence number
        count_result = client.table('messages') \
            .select('id', count='exact') \
            .eq('conversation_id', conversation_id) \
            .execute()
        next_seq = (count_result.count or 0) + 1

        # Insert user message
        client.table('messages').insert({
            'conversation_id': conversation_id,
            'user_id': user_id,
            'role': 'user',
            'content': question,
            'sequence_number': next_seq
        }).execute()

        # Insert assistant message
        client.table('messages').insert({
            'conversation_id': conversation_id,
            'user_id': user_id,
            'role': 'assistant',
            'content': answer,
            'sequence_number': next_seq + 1
        }).execute()

        logger.debug(f"Added conversation for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to add conversation: {e}")
        return False


def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Get recent conversation history for a session.

    Args:
        session_id: The chat session ID
        limit: Maximum number of message pairs to return

    Returns:
        List of conversation entries with question/answer (oldest first)
    """
    try:
        client = get_supabase_client()

        # Find conversation by session_id
        conv_result = client.table('conversations') \
            .select('id') \
            .eq('session_id', session_id) \
            .limit(1) \
            .execute()

        if not conv_result.data:
            return []

        conversation_id = conv_result.data[0]['id']

        # Get messages (most recent first, then reverse)
        result = client.table('messages') \
            .select('role, content, created_at') \
            .eq('conversation_id', conversation_id) \
            .order('sequence_number', desc=True) \
            .limit(limit * 2) \
            .execute()

        if not result.data:
            return []

        # Reverse to chronological order and pair up messages
        messages = list(reversed(result.data))
        conversations = []

        i = 0
        while i < len(messages) - 1:
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                conversations.append({
                    'question': messages[i]['content'],
                    'answer': messages[i + 1]['content'],
                    'created_at': messages[i]['created_at']
                })
                i += 2
            else:
                i += 1

        return conversations
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        return []


def clear_conversation_history(session_id: str, user_id: str) -> bool:
    """
    Clear conversation history for a session.

    Args:
        session_id: The chat session ID
        user_id: The user's UUID (for RLS)

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_supabase_client()

        # Find conversation
        conv_result = client.table('conversations') \
            .select('id') \
            .eq('session_id', session_id) \
            .eq('user_id', user_id) \
            .limit(1) \
            .execute()

        if not conv_result.data:
            return True  # Nothing to clear

        conversation_id = conv_result.data[0]['id']

        # Delete messages
        client.table('messages') \
            .delete() \
            .eq('conversation_id', conversation_id) \
            .execute()

        # Delete conversation
        client.table('conversations') \
            .delete() \
            .eq('id', conversation_id) \
            .execute()

        logger.info(f"Cleared conversation history for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {e}")
        return False
