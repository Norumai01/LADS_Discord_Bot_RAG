import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

_initialized = False

def initiateLogging (directory: str = "logs", service: str = "default"):
    """
    Configures application logging to write messages to a timestamped log file.

    Args:
        directory (str): Directory where log files will be stored. Defaults to "logs".
        service (str): Name of the service for which logs are being generated. Defaults to "default".

    Returns:
        None
    """
    global _initialized

    # Logging initialized, so we don't want to reconfigure it again.
    if _initialized:
        return

    # Checks if logging to file is enabled/disabled via env.
    writeLogs: bool = os.getenv("WRITE_LOGS_FILE", "True").lower() == "true"
    if not writeLogs:
        print("Logging to file is disabled. Logs will only be printed to console.")

    # Default console output format
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Output to console and file if enabled
    handlers = [console]

    # File output configuration, if enabled
    if writeLogs:
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        logFile = os.path.join(directory, f"log_{service}_{timestamp}.log")

        file_handler = logging.FileHandler(logFile, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        handlers.append(file_handler)

    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers
    )

    _initialized = True