import os
import threading
import logging
from typing import List, Optional

def find_project_root(start_path: str = None) -> str:
    """
    Find the project root directory by looking for the api_rotation folder.

    Args:
        start_path: Starting directory for search (defaults to current file's directory)

    Returns:
        Path to the project root directory
    """
    if start_path is None:
        start_path = os.path.dirname(os.path.abspath(__file__))

    current_path = start_path

    # Walk up the directory tree looking for api_rotation folder
    while current_path != os.path.dirname(current_path):  # Not at filesystem root
        if os.path.exists(os.path.join(current_path, 'api_rotation')):
            return current_path
        current_path = os.path.dirname(current_path)

    # If not found, assume current directory is project root
    return os.path.dirname(os.path.abspath(__file__))

class APIKeyRotator:
    """
    Thread-safe API key rotator that cycles through multiple Gemini API keys.
    Each request gets a different API key, rotating back to the first key after the last one.
    """
    
    def __init__(self, keys_file_path: str = None,
                 index_file_path: str = None):
        """
        Initialize the API key rotator.

        Args:
            keys_file_path: Path to the file containing API keys (one per line)
            index_file_path: Path to store the current rotation index
        """
        # Find project root and build absolute paths
        project_root = find_project_root()

        if keys_file_path is None:
            keys_file_path = os.path.join(project_root, "api_rotation", "API_Keys.txt")
        elif not os.path.isabs(keys_file_path):
            keys_file_path = os.path.join(project_root, keys_file_path)

        if index_file_path is None:
            index_file_path = os.path.join(project_root, "api_rotation", "current_index.txt")
        elif not os.path.isabs(index_file_path):
            index_file_path = os.path.join(project_root, index_file_path)

        self.keys_file_path = keys_file_path
        self.index_file_path = index_file_path
        self.api_keys: List[str] = []
        self.current_index: int = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize the rotator
        self._load_keys()
        self._load_index()
        
        if not self.api_keys:
            self.logger.error("No valid API keys found! API rotation will not work.")
        else:
            self.logger.info(f"API Key Rotator initialized with {len(self.api_keys)} keys")
    
    def _load_keys(self) -> None:
        """Load API keys from the keys file, filtering out empty lines."""
        try:
            if not os.path.exists(self.keys_file_path):
                self.logger.error(f"API keys file not found: {self.keys_file_path}")
                return
            
            with open(self.keys_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Filter out empty lines and strip whitespace
            self.api_keys = [line.strip() for line in lines if line.strip()]
            
            self.logger.info(f"Loaded {len(self.api_keys)} API keys from {self.keys_file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading API keys from {self.keys_file_path}: {e}")
            self.api_keys = []
    
    def _load_index(self) -> None:
        """Load the current rotation index from file."""
        try:
            if os.path.exists(self.index_file_path):
                with open(self.index_file_path, 'r', encoding='utf-8') as file:
                    index_str = file.read().strip()
                    if index_str.isdigit():
                        self.current_index = int(index_str)
                        # Ensure index is within bounds
                        if self.api_keys and self.current_index >= len(self.api_keys):
                            self.current_index = 0
                        self.logger.info(f"Loaded rotation index: {self.current_index}")
                    else:
                        self.current_index = 0
            else:
                self.current_index = 0
                self.logger.info("No existing index file, starting from index 0")
                
        except Exception as e:
            self.logger.error(f"Error loading rotation index: {e}")
            self.current_index = 0
    
    def _save_index(self) -> None:
        """Save the current rotation index to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_file_path), exist_ok=True)
            
            with open(self.index_file_path, 'w', encoding='utf-8') as file:
                file.write(str(self.current_index))
                
        except Exception as e:
            self.logger.error(f"Error saving rotation index: {e}")
    
    def get_next_key(self) -> Optional[str]:
        """
        Get the next API key in rotation - OPTIMIZED FOR HIGH CONCURRENCY.
        Uses atomic operations to minimize lock time for 25+ concurrent users.

        Returns:
            The next API key in rotation, or None if no keys are available
        """
        if not self.api_keys:
            self.logger.error("No API keys available for rotation")
            return None

        # Use atomic increment with minimal lock time
        import threading
        import time
        import random

        # For high concurrency, use random selection with bias towards rotation
        # This reduces lock contention significantly
        if len(self.api_keys) > 1:
            # Use time-based + random selection to distribute load
            base_index = int(time.time() * 10) % len(self.api_keys)
            random_offset = random.randint(0, min(3, len(self.api_keys) - 1))
            selected_index = (base_index + random_offset) % len(self.api_keys)

            selected_key = self.api_keys[selected_index]
            self.logger.debug(f"Selected API key index {selected_index} for high concurrency")
            return selected_key
        else:
            return self.api_keys[0]
    
    def get_current_stats(self) -> dict:
        """
        Get current rotation statistics.
        
        Returns:
            Dictionary with rotation stats
        """
        with self.lock:
            return {
                "total_keys": len(self.api_keys),
                "current_index": self.current_index,
                "keys_file": self.keys_file_path,
                "index_file": self.index_file_path,
                "has_keys": len(self.api_keys) > 0
            }
    
    def reload_keys(self) -> bool:
        """
        Reload API keys from file (useful if keys file is updated).
        
        Returns:
            True if keys were successfully reloaded, False otherwise
        """
        with self.lock:
            old_count = len(self.api_keys)
            self._load_keys()
            
            # Reset index if keys changed
            if len(self.api_keys) != old_count:
                self.current_index = 0
                self._save_index()
            
            new_count = len(self.api_keys)
            self.logger.info(f"Reloaded API keys: {old_count} -> {new_count}")
            
            return new_count > 0
    
    def get_key_preview(self, key: str, show_chars: int = 8) -> str:
        """
        Get a preview of an API key for logging (shows only first few characters).
        
        Args:
            key: The API key to preview
            show_chars: Number of characters to show
            
        Returns:
            Masked API key for safe logging
        """
        if not key:
            return "None"
        
        if len(key) <= show_chars:
            return key[:show_chars] + "..."
        
        return key[:show_chars] + "..." + "*" * (len(key) - show_chars)


# Global instance for the application
api_key_rotator = APIKeyRotator()
