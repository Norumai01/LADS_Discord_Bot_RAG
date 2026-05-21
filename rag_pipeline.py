import logging

logger = logging.getLogger(__name__)

def save_response(response):
    logger.info(f"Saving response: {response}")