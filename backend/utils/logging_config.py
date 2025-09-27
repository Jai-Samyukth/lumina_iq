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

        # Get raw message
        raw_message = record.getMessage()

        # Parse if structured JSON log
        actual_message = raw_message
        data = {}
        try:
            import json
            if raw_message.startswith('{') and raw_message.endswith('}') and len(raw_message) > 10:
                log_data = json.loads(raw_message)
                actual_message = log_data.get('message', raw_message)
                data = log_data.get('data', {})
        except (json.JSONDecodeError, TypeError):
            # Not JSON, use as is
            actual_message = raw_message

        # Simplify common verbose messages using actual_message and data
        shortened = actual_message

        if actual_message == "Starting PDF text extraction":
            file_path = data.get('file_path')
            if file_path:
                from pathlib import Path
                filename = Path(file_path).name
                shortened = f"Extracting: {filename}"
            else:
                shortened = "Extracting PDF"

        elif actual_message == "Cache miss - extracting text from PDF":
            shortened = "Cache miss"

        elif actual_message == "PDF loaded successfully":
            pages = data.get('pages', 0)
            shortened = f"PDF loaded ({pages} pages)"

        elif actual_message == "Text extraction completed":
            length = data.get('extracted_length', 0)
            shortened = f"Text extracted ({length:,} chars)"

        elif actual_message == "Very little text extracted":
            length = data.get('extracted_length', 0)
            shortened = f"Little text extracted ({length} chars)"

        elif actual_message == "Successfully cached extracted text":
            shortened = "Text cached"

        elif actual_message == "Using cached text":
            length = data.get('text_length', 0)
            shortened = "Using cache"

        elif actual_message == "Cache hit":
            shortened = "Cache hit"

        elif actual_message == "Successfully cached text":
            shortened = "Text cached"

        elif "Successfully generated response" in actual_message:
            # For chat service
            length = data.get('length', 0)
            shortened = f"Response generated length: {length}"

        elif actual_message == "Generating questions":
            count = data.get('count', 0)
            mode = data.get('mode', 'questions')
            if count:
                shortened = f"Generating {count} {mode} questions"
            else:
                shortened = "Generating questions"

        elif actual_message == "Gemini AI response received":
            length = data.get('response_length', 0)
            shortened = f"AI response ({length:,} chars)"

        elif "Login successful" in actual_message:
            shortened = "Login successful"

        elif "API key rotation enabled" in actual_message:
            shortened = "API rotation enabled"

        # Create compact log line
        level_short = record.levelname[0]  # Just first letter
        return f"{timestamp} [{service.upper()}] {level_short}: {shortened}"

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
