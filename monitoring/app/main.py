"""Application Entry Point"""
import os
import aiopg
import asyncio
import logging

from common.loggers.logger import init_logger
from communicators.service_communicator import ServiceCommunicator
from repositories.monitoring_pg import MonitoringRepository
from services import update_metrics


init_logger()
logger = logging.getLogger('monitoring')

ALL_PATHS = {}


async def main():

    # Repository initialization
    db_connection = await aiopg.create_pool(
        dbname=os.environ['DB_NAME'],
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ['DB_PORT'],
        minsize=3,
        maxsize=10
    )

    monitoring_repository = MonitoringRepository(conn=db_connection)
    await monitoring_repository.check_connection()

    # Service communicator initialization
    communicator = ServiceCommunicator(server_name=os.environ['SERVICE'],
                                       metric_path='/write-metric',
                                       switch_path='/switch-service')

    loop = asyncio.get_event_loop()

    while True:
        try:
            for path in await monitoring_repository.get_all_path_to_check():
                loop.create_task(
                    update_metrics(path=path,
                                   monitoring_repo=monitoring_repository,
                                   service=communicator))

        except Exception as _err:
            logger.error(f'Error in main function while processing message')
            logger.exception(_err)
            continue


if __name__ == '__main__':

    logger.info('Starting Youtube worker')
    try:
        asyncio.run(main())
    except Exception as err:
        logger.exception(err)
