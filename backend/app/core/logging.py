import logging
import os
from datetime import datetime
from threading import Lock

# Lock for thread-safe file writing
log_lock = Lock()

# Path for combined dev log file (in project root)
DEV_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'dev.log')

def clear_dev_log():
    """Clear the dev.log file"""
    try:
        with log_lock:
            open(DEV_LOG_PATH, 'w').close()
    except Exception:
        pass

def write_to_dev_log(source: str, level: str, message: str, metadata: str = None):
    """Write a log entry to dev.log file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color codes for different log levels
        level_color = {
            'debug': '\033[36m',    # Cyan
            'info': '\033[32m',     # Green
            'warning': '\033[33m',  # Yellow
            'error': '\033[31m',    # Red
        }
        
        color = level_color.get(level.lower(), '\033[0m')
        reset = '\033[0m'
        
        source_prefix = source.upper()
        level_text = f"{color}{level.upper()}{reset}"
        
        log_entry = f"{timestamp} | {source_prefix} | {level_text} | {message}"
        if metadata:
            log_entry += f" [{metadata}]"
        
        with log_lock:
            with open(DEV_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
                f.flush()
    except Exception:
        # Avoid recursion in case of logging errors
        pass


class DevLogHandler(logging.Handler):
    def emit(self, record):
        try:
            metadata = f"{record.name}:{record.lineno}"
            write_to_dev_log("backend", record.levelname.lower(), record.getMessage(), metadata)
        except Exception:
            # Avoid recursion in case of logging errors
            pass


# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Add dev log handler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(DevLogHandler())


def log_info(message: str, metadata: str = None):
    """Log info message to both file and database"""
    logger.info(message)


def log_error(message: str, metadata: str = None):
    """Log error message to both file and database"""
    logger.error(message)


def log_warning(message: str, metadata: str = None):
    """Log warning message to both file and database"""
    logger.warning(message)