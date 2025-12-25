# storage_utils.py
import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("storage_utils")
logging.basicConfig(level=logging.INFO)

class PersistentStorage:
    """Handles persistent storage of PDF chunks and patient profiles"""

    def __init__(self, storage_dir: str = "/tmp/wondr_storage"):
        self.storage_dir = storage_dir
        self.chunks_dir = os.path.join(storage_dir, "chunks")
        self.profiles_dir = os.path.join(storage_dir, "profiles")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")

        # Create directories if they don't exist
        os.makedirs(self.chunks_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)

        # Initialize or load metadata
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata about stored documents"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                return {"documents": {}, "profile": None}
        return {"documents": {}, "profile": None}

    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def save_document_chunks(self, filename: str, chunks: List[str]) -> bool:
        """
        Save chunks for a specific document
        Returns True if successful
        """
        try:
            # Create a unique ID based on filename and timestamp
            doc_id = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chunk_file = os.path.join(self.chunks_dir, f"{doc_id}.json")

            # Save chunks to file
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "filename": filename,
                    "chunks": chunks,
                    "timestamp": datetime.now().isoformat(),
                    "chunk_count": len(chunks)
                }, f, indent=2)

            # Update metadata
            self.metadata["documents"][doc_id] = {
                "filename": filename,
                "chunk_count": len(chunks),
                "timestamp": datetime.now().isoformat(),
                "chunk_file": chunk_file
            }
            self._save_metadata()

            logger.info(f"Saved {len(chunks)} chunks for {filename} with ID {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save document chunks: {e}")
            return False

    def load_all_chunks(self) -> List[str]:
        """
        Load all chunks from all stored documents
        Returns a flat list of all chunks
        """
        all_chunks = []
        try:
            for doc_id, doc_info in self.metadata["documents"].items():
                chunk_file = doc_info.get("chunk_file")
                if chunk_file and os.path.exists(chunk_file):
                    try:
                        with open(chunk_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            chunks = data.get("chunks", [])
                            all_chunks.extend(chunks)
                            logger.info(f"Loaded {len(chunks)} chunks from {doc_info['filename']}")
                    except Exception as e:
                        logger.error(f"Failed to load chunks from {chunk_file}: {e}")

            logger.info(f"Loaded total of {len(all_chunks)} chunks from {len(self.metadata['documents'])} documents")
            return all_chunks
        except Exception as e:
            logger.error(f"Failed to load all chunks: {e}")
            return []

    def get_document_list(self) -> List[Dict[str, Any]]:
        """Get list of all stored documents with metadata"""
        documents = []
        for doc_id, doc_info in self.metadata["documents"].items():
            documents.append({
                "id": doc_id,
                "filename": doc_info["filename"],
                "chunk_count": doc_info["chunk_count"],
                "timestamp": doc_info["timestamp"]
            })
        # Sort by timestamp, newest first
        documents.sort(key=lambda x: x["timestamp"], reverse=True)
        return documents

    def remove_document(self, doc_id: str) -> bool:
        """
        Remove a specific document and its chunks
        Returns True if successful
        """
        try:
            if doc_id not in self.metadata["documents"]:
                logger.warning(f"Document {doc_id} not found in metadata")
                return False

            doc_info = self.metadata["documents"][doc_id]
            chunk_file = doc_info.get("chunk_file")

            # Delete chunk file
            if chunk_file and os.path.exists(chunk_file):
                os.remove(chunk_file)
                logger.info(f"Deleted chunk file: {chunk_file}")

            # Remove from metadata
            del self.metadata["documents"][doc_id]
            self._save_metadata()

            logger.info(f"Removed document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove document {doc_id}: {e}")
            return False

    def clear_all_documents(self) -> bool:
        """
        Clear all stored documents
        Returns True if successful
        """
        try:
            # Delete all chunk files
            for doc_id, doc_info in self.metadata["documents"].items():
                chunk_file = doc_info.get("chunk_file")
                if chunk_file and os.path.exists(chunk_file):
                    try:
                        os.remove(chunk_file)
                    except Exception as e:
                        logger.error(f"Failed to delete {chunk_file}: {e}")

            # Clear metadata
            self.metadata["documents"] = {}
            self._save_metadata()

            logger.info("Cleared all documents")
            return True
        except Exception as e:
            logger.error(f"Failed to clear all documents: {e}")
            return False

    def _get_user_profile_dir(self, user_id: str = None) -> str:
        """Get profile directory for a specific user or default"""
        if user_id:
            user_dir = os.path.join(self.storage_dir, "users", user_id)
            os.makedirs(user_dir, exist_ok=True)
            return user_dir
        return self.profiles_dir

    def save_profile(self, profile: dict, user_id: str = None) -> bool:
        """
        Save patient profile for a specific user
        Returns True if successful
        """
        try:
            profile_dir = self._get_user_profile_dir(user_id)
            profile_file = os.path.join(profile_dir, "profile.json")

            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)

            logger.info(f"Saved patient profile for user {user_id or 'default'}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False

    def load_profile(self, user_id: str = None) -> dict:
        """
        Load patient profile for a specific user
        Returns profile dict or empty dict if not found
        """
        try:
            profile_dir = self._get_user_profile_dir(user_id)
            profile_file = os.path.join(profile_dir, "profile.json")

            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    logger.info(f"Loaded patient profile for user {user_id or 'default'}")
                    return profile
            return {}
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            return {}

    def clear_profile(self, user_id: str = None) -> bool:
        """
        Clear stored patient profile for a specific user
        Returns True if successful
        """
        try:
            profile_dir = self._get_user_profile_dir(user_id)
            profile_file = os.path.join(profile_dir, "profile.json")

            if os.path.exists(profile_file):
                os.remove(profile_file)
                logger.info(f"Cleared patient profile for user {user_id or 'default'}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear profile: {e}")
            return False
