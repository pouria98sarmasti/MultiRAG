"""
Logging utility for the MultiRAG application.

This module provides a configured logger that follows best practices
for application logging with rotation and formatting.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with the specified name and log level.
    
    Parameters
    ----------
    name : str
        The name of the logger, typically the module name.
    log_level : str, optional
        The logging level as a string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        Default is "INFO".
    
    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    # Create logs directory if it doesn't exist
    LOGS_DIR = Path("logs")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure log file with date
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    LOG_FILE = LOGS_DIR / f"log_{date_str}.log"
    
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())
    
    # Clear handlers if they exist
    if logger.handlers:
        logger.handlers.clear()
    
    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", backupCount=30
    )
    file_format = logging.Formatter(
        "[ %(asctime)s ] - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    
    return logger


# Default application logger
app_logger = setup_logger("multirag") 