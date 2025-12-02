"""
Logging configuration for the analyzer
"""
import logging
import sys
from datetime import datetime


class Logger:
    """Logging utility class"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name: str, level: str = 'INFO') -> logging.Logger:
        """
        Get or create a logger instance
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Logger instance
        """
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not logger.handlers:
            logger.addHandler(console_handler)
        
        Logger._loggers[name] = logger
        return logger
    
    @staticmethod
    def setup_file_logging(logger: logging.Logger, log_file: str):
        """
        Add file handler to logger
        
        Args:
            logger: Logger instance
            log_file: Path to log file
        """
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
