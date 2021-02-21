"""Abstract communicators class. Communicators are going to be used to communicate with the outer services"""
from abc import ABC
from typing import Optional

from models import ServiceResponse


class ServiceCommunicatorAbstract(ABC):
    """Server communicator"""

    async def get_metrics(self, path) -> Optional[ServiceResponse]:
        """
        Returns prepared response from Service.
        None returned if there is some kind of network error or service is down and not responding
        """
        raise NotImplemented

    async def send_metrics(self, path: str, metric: int) -> Optional[ServiceResponse]:
        """Sends metrics to the Service"""
        raise NotImplemented

    async def switch_state_for_path(self, path, status_code: int) -> Optional[ServiceResponse]:
        """Sends switch state signal to the service"""
        raise NotImplemented
