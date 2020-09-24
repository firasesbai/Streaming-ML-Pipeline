import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    """
    This function configures the logging module

    Arguments:
    logger_name -- name of the logger
    log_file -- name of the file where the logs will be saved
    level -- level or severity of the events to be logged - Default is for detailed information
    """

    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
