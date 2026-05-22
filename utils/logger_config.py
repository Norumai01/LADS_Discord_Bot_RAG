import logging
import os
from datetime import datetime
import datefmt
import fmt


def initiateLogging (directory: str = "logs", service: str = "default"):
    """
    Configures application logging to write messages to a timestamped log file.

    Args:
        directory (str): Directory where log files will be stored. Defaults to "logs".
        service (str): Name of the service for which logs are being generated. Defaults to "default".

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    logFile = os.path.join(directory, f"log_{service}_{timestamp}.log")

    formatConsole = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    dateFmtConsole = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logFile,
        filemode="a",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(formatConsole, datefmt=dateFmtConsole))
    logging.getLogger().addHandler(console)