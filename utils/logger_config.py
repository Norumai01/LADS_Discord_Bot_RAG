import logging
import os
from datetime import datetime

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

    if _initialized:
        return # Already initialized, no need to reconfigure

    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    logFile = os.path.join(directory, f"log_{service}_{timestamp}.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logFile,
        filemode="a",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logging.getLogger().addHandler(console)

    _initialized = True