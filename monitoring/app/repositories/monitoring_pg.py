"""Monitoring repository integration with PostgreSQL"""
import logging
from typing import Optional, List

import psycopg2
from aiopg import connection, cursor

from repositories.abstract import MonitoringRepositoryAbstract
from models import ServiceState, State


logger = logging.getLogger('monitoring')


class MonitoringRepository(MonitoringRepositoryAbstract):

    def __init__(self, conn: connection.Connection = None):
        self._connection = conn

    async def check_connection(self):
        """Check if database connection is active"""
        with (await self._connection.cursor()) as cur:
            await cur.execute('SELECT 1')
            try:
                res = await cur.fetchone()
                if res[0] == 1:
                    logger.info('%s: database connection is OK', self.__class__.__name__)
            except Exception as err:
                logger.error('%s: database connection failed', self.__class__.__name__)
                logger.exception(err)
                raise err

    async def save_service_state(self, state: ServiceState):
        """Save Service state to the database"""
        query = """
            INSERT INTO path_state(path, status_code, state) VALUES (%(path)s, %(status_code)s, %(state)s)
            ON CONFLICT ON CONSTRAINT path_pkey
            DO UPDATE SET 
                status_code = excluded.status_code, state = excluded.state;
        """

        try:
            with (await self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor))\
                    as cur:  # type: cursor.Cursor

                query = cur.mogrify(query, {'path': state.path,
                                            'status_code': state.status_code,
                                            'state': state.state.value})
                await cur.execute(query)

        except Exception as err:
            logger.exception(err)
            raise err

    async def get_service_state(self, path: str) -> Optional[ServiceState]:
        """Returns service states by its url"""
        query = """
            SELECT path, status_code, state, create_time, update_time FROM path_state WHERE path = %(path)s;
        """
        try:
            with (await self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor)) \
                    as cur:  # type: cursor.Cursor

                query = cur.mogrify(query, {'path': path})
                await cur.execute(query)

                result = await cur.fetchone()
                if not result:
                    return

                return ServiceState(path=result['path'],
                                    state=State(result['state']),
                                    status_code=result['status_code'],
                                    create_time=result['create_time'],
                                    update_time=result['update_time'])

        except Exception as err:
            logger.exception(err)
            raise err

    async def get_all_path_to_check(self) -> List[str]:
        """Returns all path that are needs to be checked"""
        query = """
            SELECT path FROM paths;
        """
        try:
            with (await self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor)) \
                    as cur:  # type: cursor.Cursor
                await cur.execute(query)
                return [path['path'] for path in await cur.fetchall()]

        except Exception as err:
            logger.exception(err)
            raise err
