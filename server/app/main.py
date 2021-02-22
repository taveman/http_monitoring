"""Application Entry Point"""
import logging
import asyncio
import random

from fastapi import FastAPI, status, Form

from common.loggers.logger import init_logger


init_logger()
logger = logging.getLogger('monitoring')


app = FastAPI()


@app.get('/metrics/{metric_id}')
async def all_urls():
    metric_to_return = random.randint(0, 10000)
    await asyncio.sleep(metric_to_return / 1000)
    should_be_broken = random.choice([True, False])
    if should_be_broken:
        raise status.HTTP_500_INTERNAL_SERVER_ERROR

    return metric_to_return


@app.post('/write-metric')
async def write_metrics(path: str = Form(...), metric: int = Form(...)):
    logger.debug('write_metrics: got metric for path: %s, metric: %s', path, metric)
    return status.HTTP_200_OK


@app.post('/switch-service')
async def switch_service(path: str = Form(...), status_code: int = Form(...)):
    logger.debug('switch-service: got change state for path: %s, state: %s', path, status_code)
    return status.HTTP_200_OK
