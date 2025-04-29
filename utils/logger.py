import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(log_level: str = "INFO"):
    logger = logging.getLogger("CardAssist")
    
    # Convert log_level string to logging level constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        # Create logs directory
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)

        # Create date-based subfolder (e.g., 2025-04-19)
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(logs_dir, current_date)
        os.makedirs(date_dir, exist_ok=True)

        # Create log file name based on run time (e.g., cardassist_2025-04-19_10-00-00.log)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(date_dir, f"cardassist_{current_time}.log")

        # File handler with rotation
        file_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=5)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger