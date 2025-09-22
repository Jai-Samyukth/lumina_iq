"""
Enhanced logging configuration with Rich formatting and better log management.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Suppress Google Cloud ALTS warnings at module level
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install
    from rich.theme import Theme
    RICH_AVAILABLE = True

    # Install rich traceback handler
    install(show_locals=False)

    # Custom theme for better readability
    custom_theme = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "service": "bold blue",
        "timestamp": "dim white"
    })

    console = Console(theme=custom_theme)

except ImportError:
    RICH_AVAILABLE = False
    console = None

class CompactFormatter(logging.Formatter):
    """Custom formatter for more compact, readable logs"""

    def format(self, record):
        # Create compact timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Get service name from logger name
        service = record.name.split('.')[-1] if '.' in record.name else record.name

        # Format message based on content
        message = record.getMessage()

        # Simplify common verbose messages
        if "Successfully generated response" in message:
            parts = message.split(', ')
            length_part = next((p for p in parts if 'length:' in p), '')
            message = f"Response generated {length_part}"

        elif "Starting PDF text extraction" in message:
            if "file_path" in message:
                # Extract filename from path
                import re
                path_match = re.search(r'([^\\\/]+\.pdf)', message)
                if path_match:
                    filename = path_match.group(1)
                    message = f"Extracting: {filename}"
                else:
                    message = "Extracting PDF"
            else:
                message = "Extracting PDF"

        elif "Cache hit" in message:
            message = "Cache hit"

        elif "Cache miss" in message:
            message = "Cache miss"

        elif "PDF loaded successfully" in message:
            # Extract pages info if available
            import re
            pages_match = re.search(r'"pages": (\d+)', message)
            if pages_match:
                pages = pages_match.group(1)
                message = f"PDF loaded ({pages} pages)"
            else:
                message = "PDF loaded"

        elif "Text extraction completed" in message:
            # Extract length info if available
            import re
            length_match = re.search(r'"extracted_length": (\d+)', message)
            if length_match:
                length = int(length_match.group(1))
                message = f"Text extracted ({length:,} chars)"
            else:
                message = "Text extracted"

        elif "Successfully cached text" in message:
            message = "Text cached"

        elif "Using cached text" in message:
            message = "Using cache"

        elif "Generating questions" in message:
            import re
            count_match = re.search(r'"count": (\d+)', message)
            mode_match = re.search(r'"mode": "([^"]+)"', message)
            if count_match and mode_match:
                count = count_match.group(1)
                mode = mode_match.group(1)
                message = f"Generating {count} {mode} questions"
            else:
                message = "Generating questions"

        elif "Gemini AI response received" in message:
            import re
            length_match = re.search(r'"response_length": (\d+)', message)
            if length_match:
                length = int(length_match.group(1))
                message = f"AI response ({length:,} chars)"
            else:
                message = "AI response received"

        elif "Login successful" in message:
            message = "Login successful"

        elif "API key rotation enabled" in message:
            message = "API rotation enabled"

        # Create compact log line
        level_short = record.levelname[0]  # Just first letter
        return f"{timestamp} [{service.upper()}] {level_short}: {message}"

class DeduplicatingHandler(logging.Handler):
    """Handler that prevents duplicate log messages"""

    def __init__(self, base_handler):
        super().__init__()
        self.base_handler = base_handler
        self.recent_messages = {}
        self.max_recent = 50

    def emit(self, record):
        # Create a key for deduplication
        dedupe_key = f"{record.name}:{record.levelname}:{record.getMessage()}"

        current_time = datetime.now().timestamp()

        # Check if we've seen this message recently (within 0.5 seconds)
        if dedupe_key in self.recent_messages:
            last_time = self.recent_messages[dedupe_key]
            if current_time - last_time < 0.5:
                return  # Skip duplicate

        # Update recent messages
        self.recent_messages[dedupe_key] = current_time

        # Clean old entries periodically
        if len(self.recent_messages) > self.max_recent:
            cutoff_time = current_time - 5  # Keep last 5 seconds
            self.recent_messages = {
                k: v for k, v in self.recent_messages.items()
                if v > cutoff_time
            }

        self.base_handler.emit(record)

def configure_logging():
    """Configure enhanced logging with Rich formatting"""

    # Only configure logging once per process
    if hasattr(logging, '_configured_for_multiworker'):
        return

    # Suppress noisy loggers
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    logging.getLogger('google.auth.transport').setLevel(logging.WARNING)
    logging.getLogger('google.auth._default').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    # Get worker ID from environment
    worker_id = os.getenv('UVICORN_WORKER_ID', '1')

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set up console handler only for main worker
    if worker_id == '1':
        if RICH_AVAILABLE:
            # Use Rich handler for better formatting
            rich_handler = RichHandler(
                console=console,
                show_time=False,
                show_path=False,
                show_level=False,
                rich_tracebacks=True
            )
            rich_handler.setFormatter(CompactFormatter())
            console_handler = DeduplicatingHandler(rich_handler)
        else:
            # Fallback to standard handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(CompactFormatter())
            console_handler = DeduplicatingHandler(console_handler)

        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)

    # Set up file handler (simplified)
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Configure specific loggers to prevent spam
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)

    # Mark as configured
    logging._configured_for_multiworker = True

    return worker_id

def get_logger(name: str):
    """Get a logger with enhanced configuration"""
    configure_logging()
    return logging.getLogger(name)
