"""
Logging configuration to prevent duplicate logs in multi-worker setup
"""

import logging
import os
from pathlib import Path

def configure_logging():
    """Configure logging to prevent duplicates in multi-worker environment"""
    
    # Only configure logging once per process
    if hasattr(logging, '_configured_for_multiworker'):
        return
    
    # Get worker ID from environment (uvicorn sets this)
    worker_id = os.getenv('UVICORN_WORKER_ID', '1')
    
    # Configure root logger to prevent duplicates
    root_logger = logging.getLogger()
    
    # Remove existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up console handler only for main worker
    if worker_id == '1':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Set up file handlers for all workers (with worker ID in filename)
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create separate log files for each worker
    log_file = logs_dir / f'app_worker_{worker_id}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | Worker-%(process)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set root logger level
    root_logger.setLevel(logging.INFO)
    
    # Configure specific loggers to prevent spam
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    
    # Mark as configured
    logging._configured_for_multiworker = True
    
    return worker_id

def get_worker_aware_logger(name: str):
    """Get a logger that's aware of the worker configuration"""
    configure_logging()
    return logging.getLogger(name)
