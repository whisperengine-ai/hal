"""Simple environment bootstrapper.

Loads environment variables from a .env file at repo root (and current working directory)
without overriding existing process env. Also configures Python logging.
"""
import os
import logging
from pathlib import Path


def load_env():
    try:
        from dotenv import load_dotenv
    except Exception:
        return  # dotenv not installed; skip silently

    # Load .env from repository root (this file's directory)
    try:
        root_env = Path(__file__).resolve().parent / ".env"
        load_dotenv(dotenv_path=root_env, override=False)
    except Exception:
        pass

    # Also load from CWD if present
    try:
        load_dotenv(override=False)
    except Exception:
        pass


def configure_logging():
    """Configure structured logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", None)
    
    # Map string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = level_map.get(log_level, logging.INFO)
    
    # Configure root logger
    handlers = []
    
    # Console handler with colored output (if available)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    handlers.append(console_handler)
    
    # File handler if LOG_FILE is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_format = logging.Formatter(
                '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )


# Execute on import
load_env()
configure_logging()
