import logging
from typing import Optional

import aiohttp

from models import ServiceResponse
from communicators.abstract import ServiceCommunicatorAbstract


logger = logging.getLogger('monitoring')


class ServiceCommunicator(ServiceCommunicatorAbstract):

    def __init__(self, server_name: str, metric_path: str, switch_path: str):
        self._server_name = server_name
        self._metric_path = f'{self._server_name}{metric_path}'
        self._switch_path = f'{self._server_name}{switch_path}'

    async def get_metrics(self, path) -> Optional[ServiceResponse]:
        """
        Returns prepared response from Service.
        None returned if there is some kind of network error or service is down and not responding
        """
        try:
            url_to_get_metrics_from = f'{self._server_name}{path}'
            logger.debug('%s: getting metrics from %s', self.__class__.__name__, url_to_get_metrics_from)

            async with aiohttp.ClientSession() as session:
                response = await session.get(url=url_to_get_metrics_from)
                if response.status != 200:
                    return ServiceResponse(path=path, status_code=response.status)
                return ServiceResponse(path=path, status_code=response.status, metric=int(await response.text()))

        except Exception as err:
            logger.error('%s: Got error while requesting metrics: %s', self.__class__.__name__, err)
            logger.exception(err)

    async def send_metrics(self, path: str, metric: int) -> Optional[ServiceResponse]:
        """Sends metrics to the Service"""
        try:
            logger.debug('%s: sending metrics: %s for path: %s', self.__class__.__name__, metric, path)

            async with aiohttp.ClientSession() as session:
                response = await session.post(url=self._metric_path, data={'path': path, 'metric': metric})
                return ServiceResponse(path=path, status_code=response.status)

        except Exception as err:
            logger.error('%s: Got error while sending metrics: %s for path: %s. Error: %s',
                         self.__class__.__name__, metric, path, err)
            logger.exception(err)

    async def switch_state_for_path(self, path, status_code: int) -> Optional[ServiceResponse]:
        """Sends request to switch state for the path on the server"""
        try:
            logger.debug('%s: sending switch event for status code: %s for path: %s',
                         self.__class__.__name__, status_code, path)

            async with aiohttp.ClientSession() as session:
                response = await session.post(url=self._switch_path, data={'path': path, 'status_code': status_code})
                return ServiceResponse(path=path, status_code=response.status)

        except Exception as err:
            logger.error('%s: Got error while sending switch event for path: %s status code: %s. Error: %s',
                         self.__class__.__name__, status_code, path, err)
            logger.exception(err)
