from typing import Optional, Dict

import pytest

from services import update_metrics
from repositories.abstract import MonitoringRepositoryAbstract
from communicators.abstract import ServiceCommunicatorAbstract
from models import ServiceState, ServiceResponse, State


class MonitoringRepositoryStub(MonitoringRepositoryAbstract):

    def __init__(self, data: Optional[Dict[str, ServiceState]] = None):
        self._data = data if data else {}

    async def save_service_state(self, state: ServiceState):
        """Save Service state to the database"""
        self._data[state.path] = state

    async def get_service_state(self, path: str) -> Optional[ServiceState]:
        """Returns service states by its url"""
        return self._data.get(path)


class ServiceCommunicatorStub(ServiceCommunicatorAbstract):

    def __init__(self):
        self._metric_requests = {}
        self._switch_requests = {}

    async def get_metrics(self, path) -> Optional[ServiceResponse]:
        """
        Returns prepared response from Service.
        None returned if there is some kind of network error or service is down and not responding
        """
        responses = {
            '/test/1': ServiceResponse(path='/test/1', status_code=200, metric=100),
            '/test/2': ServiceResponse(path='/test/2', status_code=400, metric=None),
            '/test/3': ServiceResponse(path='/test/3', status_code=500, metric=None),
            '/test/4': None
        }
        return responses.get(path)

    async def send_metrics(self, path: str, metric: int) -> Optional[ServiceResponse]:
        """Sends metrics to the Service"""
        self._metric_requests[path] = metric
        responses = {
            '/test/1': ServiceResponse(path='/test/1', status_code=200, metric=None),
            '/test/2': ServiceResponse(path='/test/2', status_code=200, metric=None),
            '/test/3': ServiceResponse(path='/test/3', status_code=400, metric=None),
        }
        return responses.get(path)

    async def switch_state_for_path(self, path, status_code: int):
        """Sends switch state signal to the service"""
        self._switch_requests[path] = status_code
        responses = {
            '/test/1': ServiceResponse(path='/test/1', status_code=200, metric=None),
            '/test/2': ServiceResponse(path='/test/2', status_code=200, metric=None),
            '/test/3': ServiceResponse(path='/test/3', status_code=500, metric=None),
        }
        return responses.get(path)


@pytest.mark.asyncio
async def test_update_metrics_service_works_as_expected_if_all_services_are_up():
    """If all services are running we should get the normal data workflow"""
    target_path = '/test/1'
    monitoring_repo = MonitoringRepositoryStub()
    service_communicator = ServiceCommunicatorStub()
    await update_metrics(path=target_path, monitoring_repo=monitoring_repo, service=service_communicator)

    # checking if we have all expected records in the repository
    assert len(monitoring_repo._data) == 1
    assert monitoring_repo._data.get(target_path).state == State.WORKING
    assert monitoring_repo._data.get(target_path).status_code == 200
    assert monitoring_repo._data.get(target_path).path == target_path
    prev_update_time = monitoring_repo._data.get(target_path).update_time

    # checking that all requests was done against service

    # metric was sent
    assert service_communicator._metric_requests[target_path] == 100

    # switch url was triggered
    assert service_communicator._switch_requests[target_path] == 200

    # if we still get 200 status code state should not changed
    await update_metrics(path=target_path, monitoring_repo=monitoring_repo, service=service_communicator)
    assert monitoring_repo._data.get(target_path).update_time == prev_update_time


@pytest.mark.asyncio
async def test_update_metrics_service_changes_state_if_we_dont_get_200_response():
    """If we do not get any code but 200 we need to change state to Failed and send HTTP request to switch endpoint"""
    target_path = '/test/2'
    monitoring_repo = MonitoringRepositoryStub()
    service_communicator = ServiceCommunicatorStub()

    # setting up record so it looks like we already have record in the repository for the target path and it was fine
    monitoring_repo._data[target_path] = ServiceState(path=target_path, state=State.WORKING, status_code=200)
    await update_metrics(path=target_path, monitoring_repo=monitoring_repo, service=service_communicator)

    # checking that we have triggered service by it's switch endpoint and that was successful
    assert service_communicator._switch_requests[target_path] == monitoring_repo._data[target_path].status_code

    # checking that we changed state in the repository afterwards
    assert monitoring_repo._data[target_path].state == State.FAILED


@pytest.mark.asyncio
async def test_update_metrics_service_does_not_change_repository_state_if_switch_endpoint_is_down():
    """
    If we dont get response or response code is not 200 from
    the switch endpoint we does not change the state in the local repository
    """
    target_path = '/test/3'
    initial_status_code = 200
    monitoring_repo = MonitoringRepositoryStub()
    service_communicator = ServiceCommunicatorStub()

    # setting up record so it looks like we already have record in the repository for the target path and it was fine
    monitoring_repo._data[target_path] = ServiceState(path=target_path,
                                                      state=State.WORKING,
                                                      status_code=initial_status_code)
    await update_metrics(path=target_path, monitoring_repo=monitoring_repo, service=service_communicator)

    # we check we that we hit switch endpoint with status code 400 that we got from metrics
    assert service_communicator._switch_requests[target_path] == 500

    # checking that we do not change state in the repository afterwards because
    # switch endpoint was down and we will inform it later
    assert monitoring_repo._data[target_path].state == State.WORKING
    assert monitoring_repo._data[target_path].status_code == initial_status_code


@pytest.mark.asyncio
async def test_update_metrics_service_does_not_change_repository_and_dont_hit_service_endpoints():
    """
    If we try to get metrics from endpoint and we fail to get any response
    for some reason (network or service is down) we do not hit anything else we just finishing a task
    """
    target_path = '/test/4'
    monitoring_repo = MonitoringRepositoryStub()
    service_communicator = ServiceCommunicatorStub()

    await update_metrics(path=target_path, monitoring_repo=monitoring_repo, service=service_communicator)

    # we do not hit switch endpoint
    assert len(service_communicator._switch_requests) == 0

    # we do not hit send metrics endpoint
    assert len(service_communicator._metric_requests) == 0

    # we do not touch repository
    assert len(monitoring_repo._data) == 0
