import logging

def get_logger(name: str, _format: str):
    handler = logging.StreamHandler()
    formatter = logging.Formatter(_format)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

BASIC_LOGGING_FORMAT="%(asctime)s - %(name)s - %(levelname)s : %(message)s"
THREAD_LOGGING_FORMAT="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s : %(message)s"

main_logger = get_logger(name="main", _format=BASIC_LOGGING_FORMAT)
thread_logger = get_logger(name="thread", _format=THREAD_LOGGING_FORMAT)