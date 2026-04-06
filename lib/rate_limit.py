"""
Rate Limiting for WondrLink

Uses Supabase to track request counts per user per endpoint.
Works with Vercel's stateless serverless architecture.
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple

logger = logging.getLogger(__name__)


def check_rate_limit(identifier: str, endpoint: str,
                     max_requests: int, window_minutes: int) -> Tuple[bool, int]:
    """
    Check if a request is within rate limits.

    Args:
        identifier: User ID or IP address
        endpoint: The API endpoint being accessed
        max_requests: Maximum requests allowed in the window
        window_minutes: Time window in minutes

    Returns:
        Tuple of (allowed: bool, remaining: int)
    """
    try:
        from supabase_client import get_admin_client
        client = get_admin_client()

        window_start = (datetime.utcnow() - timedelta(minutes=window_minutes)).isoformat()

        # Count recent requests
        result = client.table('rate_limits') \
            .select('id', count='exact') \
            .eq('identifier', identifier) \
            .eq('endpoint', endpoint) \
            .gte('created_at', window_start) \
            .execute()

        current_count = result.count or 0
        remaining = max(0, max_requests - current_count)

        if current_count >= max_requests:
            logger.warning(f"Rate limit exceeded: {identifier} on {endpoint} ({current_count}/{max_requests})")
            return False, 0

        # Record this request
        client.table('rate_limits').insert({
            'identifier': identifier,
            'endpoint': endpoint
        }).execute()

        return True, remaining - 1

    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        # Fail open — don't block requests if rate limiting breaks
        return True, max_requests
