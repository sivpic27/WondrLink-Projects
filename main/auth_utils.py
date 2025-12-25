# auth_utils.py
import os
import json
import uuid
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger("auth_utils")

USERS_FILE = "/tmp/wondr_storage/users.json"

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load users: {e}")
    return {"users": {}}

def save_users(data):
    """Save users to JSON file"""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save users: {e}")
        return False

def create_user(username: str, password: str):
    """
    Create a new user account.
    Returns: (user_id, error_message)
    """
    if not username or not password:
        return None, "Username and password are required"

    if len(username) < 3:
        return None, "Username must be at least 3 characters"

    if len(password) < 4:
        return None, "Password must be at least 4 characters"

    data = load_users()

    # Check if username exists
    for user in data["users"].values():
        if user["username"].lower() == username.lower():
            return None, "Username already exists"

    # Create new user
    user_id = str(uuid.uuid4())[:8]
    data["users"][user_id] = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.now().isoformat()
    }

    if save_users(data):
        logger.info(f"Created new user: {username} (ID: {user_id})")
        return user_id, None
    else:
        return None, "Failed to save user"

def authenticate_user(username: str, password: str):
    """
    Authenticate a user with username and password.
    Returns: (user_id, username) if successful, (None, None) if failed
    """
    if not username or not password:
        return None, None

    data = load_users()

    for user_id, user in data["users"].items():
        if user["username"].lower() == username.lower():
            if check_password_hash(user["password_hash"], password):
                logger.info(f"User authenticated: {username}")
                return user_id, user["username"]
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                return None, None

    logger.warning(f"Login attempt for non-existent user: {username}")
    return None, None

def get_user(user_id: str):
    """Get user info by user_id (excludes password hash)"""
    if not user_id:
        return None

    data = load_users()
    user = data["users"].get(user_id)

    if user:
        # Return user info without password hash
        return {
            "user_id": user_id,
            "username": user["username"],
            "created_at": user.get("created_at")
        }
    return None

def get_user_directory(user_id: str) -> str:
    """Get the storage directory path for a specific user"""
    return f"/tmp/wondr_storage/users/{user_id}"
