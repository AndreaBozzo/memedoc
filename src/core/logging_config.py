import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

class MemeDocLogger:
    """Structured logging for MemeDoc with performance tracking"""

    def __init__(self, name: str = 'memedoc', log_level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers with structured formatting"""
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # File handler with rotation
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/memedoc.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log_scraping_start(self, platform: str, limit: int):
        """Log scraping session start"""
        self.logger.info(f"Starting scraping session | Platform: {platform} | Limit: {limit}")

    def log_scraping_result(self, platform: str, total: int, new: int, processing_time: float):
        """Log scraping results with performance metrics"""
        rate = total / processing_time if processing_time > 0 else 0
        self.logger.info(
            f"Scraping completed | Platform: {platform} | "
            f"Total: {total} | New: {new} | "
            f"Time: {processing_time:.2f}s | Rate: {rate:.1f} posts/s"
        )

    def log_image_processing(self, url: str, success: bool, processing_time: Optional[float] = None):
        """Log image processing results"""
        if success:
            time_info = f" | Time: {processing_time:.2f}s" if processing_time else ""
            self.logger.debug(f"Image processed successfully | URL: {url}{time_info}")
        else:
            self.logger.warning(f"Image processing failed | URL: {url}")

    def log_database_operation(self, operation: str, count: int, success: bool, execution_time: float):
        """Log database operations with performance"""
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        self.logger.log(
            level,
            f"Database {operation} | Count: {count} | "
            f"Status: {status} | Time: {execution_time:.2f}s"
        )

    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        context_info = f" | Context: {context}" if context else ""
        self.logger.error(f"Error occurred | {type(error).__name__}: {str(error)}{context_info}")

    def log_performance_warning(self, metric: str, value: float, threshold: float):
        """Log performance warnings"""
        self.logger.warning(
            f"Performance warning | {metric}: {value:.2f} | Threshold: {threshold:.2f}"
        )

# Global logger instance
logger = MemeDocLogger()

# Convenience functions
def log_info(message: str):
    logger.logger.info(message)

def log_warning(message: str):
    logger.logger.warning(message)

def log_error(message: str):
    logger.logger.error(message)

def log_debug(message: str):
    logger.logger.debug(message)