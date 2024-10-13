import logging
import datetime
import os


def setup_logger():
    log_directory = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_directory):
        os.mkdir(log_directory)
    log_file_name = os.path.join(log_directory, f'session_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log')

    formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style="{")

    file_handler = logging.FileHandler(log_file_name, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger('happy_little_bot')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
