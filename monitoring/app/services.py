import logging
from datetime import datetime
from functools import wraps

from models import ServiceState, State
from repositories.abstract import MonitoringRepositoryAbstract
from communicators.abstract import ServiceCommunicatorAbstract


logger = logging.getLogger('monitoring')


def limiter(fn):
    """Limits requests so they do not run in a less than 1 second interval"""
    all_paths = {}

    @wraps(fn)
    async def wrapper(path, *args, **kwargs):
        last_run_time = all_paths.get(path)
        current_time = datetime.utcnow().timestamp()

        # if time passed less than 1 second, skip the decorated function call
        if last_run_time and current_time - last_run_time < 1:
            return

        all_paths[path] = current_time
        return await fn(path, *args, **kwargs)

    return wrapper


@limiter
async def update_metrics(path: str,
                         monitoring_repo: MonitoringRepositoryAbstract,
                         service: ServiceCommunicatorAbstract):
    """Gets metrics from the service and sends them to the outer """
    try:
        previous_path_state = await monitoring_repo.get_service_state(path=path)
        service_response = await service.get_metrics(path=path)

        # if we do not get any response from the service there is nothing we can do - will try again later
        if not service_response:
            logger.error('update_metrics: No response from %s while getting metrics', path)
            return

        current_path_state = ServiceState(path=path,
                                          state=State.WORKING,
                                          status_code=service_response.status_code)

        if service_response.status_code != 200:
            logger.debug('update_metrics: path %s has error: %s', path, service_response.status_code)
            current_path_state.state = State.FAILED

        else:
            service_response = await service.send_metrics(path=path, metric=service_response.metric)
            # if we do not get response while sending metrics back we still want to know if path state was changed
            if not service_response:
                logger.error('update_metrics: No response from %s while sending metrics', path)

        if not previous_path_state or previous_path_state.state != current_path_state.state:
            response = await service.switch_state_for_path(path=path, status_code=current_path_state.status_code)
            if not response or response.status_code != 200:
                return
            # updating local service state only when we successfully informed the service itself
            await monitoring_repo.save_service_state(state=current_path_state)

    except Exception as err:
        logger.error('update_metrics: Got unexpected error: %s', err)
        logger.exception(err)
