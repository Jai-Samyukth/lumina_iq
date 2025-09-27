import os
import sys
from api_key_rotator import api_key_rotator

def setup_api_rotation_database():
    """
    Setup the SQLite database for API key rotation.
    This script creates the database, migrates data from text files,
    and verifies the setup.
    """
    print("Setting up API key rotation database...")
    
    # The rotator automatically sets up the database and migrates data
    # when initialized. Here we trigger reload to ensure everything is loaded.
    print("1. Initializing API key rotator...")
    if not api_key_rotator.api_keys:
        print("Warning: No API keys loaded. Check API_Keys.txt file.")
        return False
    
    print(f"2. Database setup completed. Loaded {len(api_key_rotator.api_keys)} API keys.")
    
    # Get stats to verify
    stats = api_key_rotator.get_current_stats()
    print(f"3. Current stats: {stats}")
    
    # Reload to ensure migration happened
    if api_key_rotator.reload_keys():
        print("4. Database reload successful.")
    else:
        print("Warning: Database reload failed.")
    
    print("\nSetup complete! The server will now use the SQLite database for API rotation.")
    print("Database location:", stats.get('database_path', 'api_rotation/api_rotation.db'))
    print("\nYou can safely remove the text files after verification, but it's optional.")
    print("The API rotator handles both files and database, preferring the database.")
    
    return True

if __name__ == "__main__":
    # Add parent directory to path if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    
    success = setup_api_rotation_database()
    if success:
        print("\nSuccess: API rotation database setup successful!")
    else:
        print("\nFailed: Setup failed. Check logs and files.")