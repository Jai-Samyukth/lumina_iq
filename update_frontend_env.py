#!/usr/bin/env python3
"""
Standalone script to update frontend .env file with current IP address.

This script can be run independently to update the frontend .env file
with the current machine's IP address.

Usage:
    python update_frontend_env.py
    python update_frontend_env.py --port 8000
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from utils.ip_detector import setup_frontend_env


def main():
    """Main function to run the IP detection and frontend env update."""
    parser = argparse.ArgumentParser(
        description="Update frontend .env file with current IP address"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Backend port number (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print("🔧 Frontend Environment Updater")
    print("=" * 40)
    
    try:
        detected_ip = setup_frontend_env(args.port)
        print(f"\n🎉 Success! Frontend will now connect to: http://{detected_ip}:{args.port}")
        print("\n💡 Tips:")
        print("   • This script runs automatically when you start the backend server")
        print("   • Run this script manually if you need to update the IP without starting the server")
        print("   • Make sure your frontend is configured to read from the .env file")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
