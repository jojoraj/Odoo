import logging

from mygeotab.exceptions import MyGeotabException
from odoo import fields, models
from odoo.tools import config

from ..services import evtc_service

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_DB = config.get('redis_db', 0)
REDIS_PWD = config.get('redis_password', '')
REDIS_USR = config.get('redis_user', '')

REDIS_EVTC = evtc_service.EvtcService(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
_logger = logging.Logger(__name__)


class Reservation(models.Model):
    _name = 'evtc.front'
    _description = 'e-vtc reservation'

    name = fields.Char()

    def btn_done_click(self):
        self.state = 'done'

    def get_reservation_information(self, pickup_point, storage_point):
        result = list()
        if not pickup_point and not storage_point:
            return
        point = [pickup_point, storage_point]
        adress = REDIS_EVTC.get_coordinates(point)
        for index, address in enumerate(adress):
            if address:
                result.append({'coordinate': {'x': address['x'], 'y': address['y'], 'description': point[index]}})
        try:
            if result:
                directions = REDIS_EVTC.get_directions(result)
                if directions and directions['legs'] and len(directions['legs']) > 0:
                    leg = directions['legs'][0]
                    return [result, [leg['distance'], leg['duration']]]
        except MyGeotabException as e:
            _logger.error(str(e))

    def get_point_lat_long(self, address):
        result = list()
        if not address:
            return result
        adress = REDIS_EVTC.get_coordinates([address])
        for _index, address in enumerate(adress):
            if address:
                result.append({'x': address['x'], 'y': address['y']})
        return result

    # get adress with lat and long
    def get_new_adress_with_latLng(self, coordinate):
        lat = coordinate.get('lat')
        lng = coordinate.get('lng')
        return REDIS_EVTC.get_address(x=lng, y=lat)
