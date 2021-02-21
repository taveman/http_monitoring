"""Abstract classes for repositories"""
from abc import ABC
from typing import Optional

from models import ServiceState


class MonitoringRepositoryAbstract(ABC):
    """Keeps all the data for the monitoring application"""

    async def save_service_state(self, state: ServiceState):
        """Save Service state to the database"""
        raise NotImplemented

    async def get_service_state(self, path: str) -> Optional[ServiceState]:
        """Returns service states by its url"""
        raise NotImplemented
