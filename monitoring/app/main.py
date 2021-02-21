"""Application Entry Point"""
import time
import logging

from common.loggers.logger import init_logger


init_logger()
logger = logging.getLogger('monitoring')


if __name__ == '__main__':
    while 1:
        logger.info('I am up and running')
        time.sleep(2)
