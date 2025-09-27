import os
import sqlite3
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
        self.db_path = os.path.join(project_root, "api_rotation", "api_rotation.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.api_keys: List[str] = []
        self.current_index: int = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
         
        # Setup database and migrate if needed
        self._setup_database()
        self._migrate_from_files()
         
        # Initialize the rotator
        self._load_keys()
        self._load_index()
         
        if not self.api_keys:
            self.logger.error("No valid API keys found! API rotation will not work.")
        else:
            self.logger.info(f"API Key Rotator initialized with {len(self.api_keys)} keys")
    
    def _setup_database(self) -> None:
        """Setup SQLite database tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        self.logger.info(f"Database setup completed at {self.db_path}")

    def _migrate_from_files(self) -> None:
        """Migrate data from files to database if database is empty."""
        cursor = self.conn.cursor()
        
        # Migrate API keys
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        if cursor.fetchone()[0] == 0 and os.path.exists(self.keys_file_path):
            try:
                with open(self.keys_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                keys = [line.strip() for line in lines if line.strip()]
                inserted = 0
                for key in keys:
                    try:
                        cursor.execute("INSERT INTO api_keys (api_key) VALUES (?)", (key,))
                        inserted += 1
                    except sqlite3.IntegrityError:
                        pass  # Key already exists
                self.conn.commit()
                self.logger.info(f"Migrated {inserted} API keys from {self.keys_file_path} to database")
            except Exception as e:
                self.logger.error(f"Error migrating API keys: {e}")
        
        # Migrate current index
        cursor.execute("SELECT value FROM config WHERE key='current_index'")
        result = cursor.fetchone()
        if result is None and os.path.exists(self.index_file_path):
            try:
                with open(self.index_file_path, 'r', encoding='utf-8') as f:
                    index_str = f.read().strip()
                if index_str.isdigit():
                    cursor.execute("INSERT INTO config (key, value) VALUES ('current_index', ?)", (index_str,))
                    self.conn.commit()
                    self.logger.info(f"Migrated current index {index_str} from {self.index_file_path} to database")
            except Exception as e:
                self.logger.error(f"Error migrating current index: {e}")

    def _load_keys(self) -> None:
        """Load API keys from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT api_key FROM api_keys ORDER BY id ASC")
            self.api_keys = [row[0] for row in cursor.fetchall()]
            self.logger.info(f"Loaded {len(self.api_keys)} API keys from database")
        except Exception as e:
            self.logger.error(f"Error loading API keys from database: {e}")
            self.api_keys = []
    
    def _load_index(self) -> None:
        """Load the current rotation index from database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key='current_index'")
            result = cursor.fetchone()
            if result and result[0].isdigit():
                self.current_index = int(result[0])
                # Ensure index is within bounds
                if self.api_keys and self.current_index >= len(self.api_keys):
                    self.current_index = 0
                    self._save_index()
                self.logger.info(f"Loaded rotation index from database: {self.current_index}")
            else:
                self.current_index = 0
                self.logger.info("No current index found in database, starting from index 0")
        except Exception as e:
            self.logger.error(f"Error loading rotation index from database: {e}")
            self.current_index = 0
    
    def _save_index(self) -> None:
        """Save the current rotation index to database."""
        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('current_index', ?)",
                              (str(self.current_index),))
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error saving rotation index to database: {e}")
    
    def get_next_key(self) -> Optional[str]:
        """
        Get the next API key in rotation - OPTIMIZED FOR HIGH CONCURRENCY.
        Uses atomic database operations with minimal lock time for 25+ concurrent users.
        Implements true round-robin rotation for even load distribution.
 
        Returns:
            The next API key in rotation, or None if no keys are available
        """
        if not self.api_keys:
            self.logger.error("No API keys available for rotation")
            return None
 
        with self.lock:
            cursor = self.conn.cursor()
            
            # Get current index atomically
            cursor.execute("SELECT value FROM config WHERE key='current_index'")
            result = cursor.fetchone()
            if result and result[0].isdigit():
                current_idx = int(result[0])
            else:
                current_idx = 0
            
            # Ensure index in bounds
            num_keys = len(self.api_keys)
            if num_keys == 0:
                return None
            if current_idx >= num_keys:
                current_idx = 0
            
            # Get the key at current index (api_keys ordered by db id)
            selected_key = self.api_keys[current_idx]
            
            # Calculate next index (round-robin)
            new_index = (current_idx + 1) % num_keys
            
            # Save new index atomically
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('current_index', ?)",
                          (str(new_index),))
            self.conn.commit()
            
            # Update in-memory index for consistency
            self.current_index = new_index
            
            self.logger.debug(f"Rotated to API key index {current_idx}, next index {new_index}")
            return selected_key
    
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
                "database_path": self.db_path,
                "has_keys": len(self.api_keys) > 0
            }
    
    def reload_keys(self) -> bool:
        """
        Reload API keys from database (useful if keys are updated in database).
         
        Returns:
            True if keys were successfully reloaded, False otherwise
        """
        with self.lock:
            old_count = len(self.api_keys)
            self._load_keys()
            self._load_index()
             
            # Reset index if keys count changed
            if len(self.api_keys) != old_count:
                self.current_index = 0
                self._save_index()
             
            new_count = len(self.api_keys)
            self.logger.info(f"Reloaded API keys from database: {old_count} -> {new_count}")
             
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


    def close(self):
        """Close the database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
            self.logger.info("Database connection closed")
 
 
# Global instance for the application
api_key_rotator = APIKeyRotator()
