# supabase_client.py
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")

_client: Client = None
_admin_client: Client = None


def get_supabase_client() -> Client:
    """
    Get the Supabase client using the anon key.
    Used for client-side operations with RLS.
    """
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        _client = create_client(url, key)
        logger.info("Supabase client initialized")

    return _client


def get_admin_client() -> Client:
    """
    Get the Supabase admin client using the service role key.
    Used for admin operations that bypass RLS.
    """
    global _admin_client
    if _admin_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        _admin_client = create_client(url, key)
        logger.info("Supabase admin client initialized")

    return _admin_client


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return user info.
    Returns user dict if valid, None if invalid.
    """
    try:
        client = get_supabase_client()
        user_response = client.auth.get_user(token)
        if user_response and user_response.user:
            return {
                "user_id": user_response.user.id,
                "email": user_response.user.email,
                "created_at": str(user_response.user.created_at) if user_response.user.created_at else None
            }
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
    return None
