import logging
import os
from datetime import datetime


def initiateLogging (directory: str = "logs"):
    """
    Configures application logging to write messages to a timestamped log file.

    Args:
        directory (str): Directory where log files will be stored. Defaults to "logs".

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    logFile = os.path.join(directory, f"log_{timestamp}.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logFile,
        filemode="a",
    )