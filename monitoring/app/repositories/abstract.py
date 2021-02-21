"""Abstract classes for repositories"""
from abc import ABC
from typing import Optional, List

from models import ServiceState


class MonitoringRepositoryAbstract(ABC):
    """Keeps all the data for the monitoring application"""

    async def save_service_state(self, state: ServiceState):
        """Save Service state to the database"""
        raise NotImplemented

    async def get_service_state(self, path: str) -> Optional[ServiceState]:
        """Returns service states by its url"""
        raise NotImplemented

    async def get_all_path_to_check(self) -> List[str]:
        """Returns all path that are needs to be checked"""
        raise NotImplemented
