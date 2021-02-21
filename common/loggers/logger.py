"""
Logger initializer
"""

import os
import logging.config
import yaml


def init_logger():
    """
    Initialize logger
    """
    logger_config_file = '/app/logger.yml'

    with open(logger_config_file, 'rt') as _file:
        config = yaml.safe_load(_file.read())

    logging.config.dictConfig(config)

    if os.environ.get('DEBUG'):
        logger = logging.getLogger('monitoring')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging._handlers.get('console'))
        logger.debug('DEBUG logging is on')
