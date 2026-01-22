import logging
from colorama import Fore, Style

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"%(asctime)s | {Fore.CYAN}%(name)s{Style.RESET_ALL} | %(levelname)s | %(message)s",
            "%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
