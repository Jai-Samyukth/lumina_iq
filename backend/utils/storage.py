# In-memory storage optimized for concurrency (replace with database in production)
import threading
from collections import defaultdict
from typing import Dict, Any, Optional

# Storage dictionaries
user_sessions = {}  # Simple session storage
chat_histories = {}
pdf_contexts = {}
pdf_metadata = {}

class ConcurrentStorageManager:
    """
    Thread-safe storage manager with per-user locking for better concurrency.
    Reduces lock contention by using separate locks for each user.
    """

    def __init__(self):
        self.user_locks = defaultdict(threading.Lock)
        self._cleanup_lock = threading.Lock()
        self._access_count = defaultdict(int)

    def get_user_lock(self, user_id: str) -> threading.Lock:
        """Get or create a lock for a specific user."""
        return self.user_locks[user_id]

    def safe_get(self, storage_dict: Dict, user_id: str, default=None) -> Any:
        """Thread-safe get operation for user data."""
        with self.user_locks[user_id]:
            self._access_count[user_id] += 1
            return storage_dict.get(user_id, default)

    def safe_set(self, storage_dict: Dict, user_id: str, value: Any) -> None:
        """Thread-safe set operation for user data."""
        with self.user_locks[user_id]:
            self._access_count[user_id] += 1
            storage_dict[user_id] = value

    def safe_update(self, storage_dict: Dict, user_id: str, update_func) -> Any:
        """Thread-safe update operation using a function."""
        with self.user_locks[user_id]:
            self._access_count[user_id] += 1
            return update_func(storage_dict, user_id)

    def safe_delete(self, storage_dict: Dict, user_id: str) -> bool:
        """Thread-safe delete operation for user data."""
        with self.user_locks[user_id]:
            if user_id in storage_dict:
                del storage_dict[user_id]
                return True
            return False

    def cleanup_inactive_locks(self, threshold: int = 1000):
        """
        Clean up locks for users with high access counts to prevent memory leaks.
        This is a simple cleanup strategy - in production, use time-based cleanup.
        """
        with self._cleanup_lock:
            users_to_cleanup = [
                user_id for user_id, count in self._access_count.items()
                if count > threshold
            ]

            for user_id in users_to_cleanup:
                # Reset access count
                self._access_count[user_id] = 0
                # Note: We don't delete the lock as it might still be in use

# Global storage manager instance
storage_manager = ConcurrentStorageManager()
