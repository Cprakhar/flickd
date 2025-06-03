import os
import logging


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    os.makedirs('logs', exist_ok=True)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('logs/flickd.log')

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')


    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    logger.propagate = False
    return logger