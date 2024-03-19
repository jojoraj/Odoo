"""
    Manipulate geotab and redis services
"""

import json
import logging

import mygeotab
from odoo import _
from odoo.exceptions import AccessDenied

from . import geotab_service, redis_service

_logger = logging.getLogger(__name__)


class EvtcService:

    def __init__(self, host, port, db=0, password=None, username=None):
        if not password and not username:
            self.redis = redis_service.RedisService(host=host, port=port, db=db)
        else:
            self.redis = redis_service.RedisService(host=host, port=port, db=db, password=password, username=username)
        self._init_geotab()

    def _init_geotab(self):
        if self.redis:
            self.credentials = json.loads(self.redis.get('credentials'))
            try:
                self.geotab = geotab_service.MyGeotabService(username=self.credentials['username'], database=self.credentials['database'],
                                                             server=self.credentials['server'], session_id=self.credentials['session_id'])
            except mygeotab.exceptions.AuthenticationException as ex:
                _logger.exception(ex)
                raise AccessDenied(_('Could not connect to redis server')) from ex

    def get_coordinates(self, addresses):
        return self.geotab.get_coordinates(addresses)

    def get_address(self, x, y):
        return self.geotab.get_address(x, y)

    def get_directions(self, way_points):
        return self.geotab.get_directions(way_points)

    def get_total_distance(self, device_id, from_date, to_date):
        return self.geotab.get_total_distance(device_id, from_date, to_date)
