# Part of Odoo. See LICENSE file for full copyright and licensing details.


import ast
import logging
import time

import redis
from odoo import api, fields, models
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_DB = config.get('redis_db', 0)
REDIS_PASSWORD = config.get('redis_password', '')
REDIS_USR = config.get('redis_user', '')

_logger = logging.getLogger(__name__)


def redis_with_user():
    try:
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, username=REDIS_USR)
    except Exception:
        _logger.error('connection to redis with user: {REDIS_USR} failed \n {e}')


def redis_without_user():
    try:
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    except Exception:
        _logger.error('connection to redis failed \n {e}')


def _connect_redis():
    return redis_with_user() if REDIS_PASSWORD or REDIS_USR else redis_without_user()


def depackage_utf_status():
    from_response = dict(status=200, values='')
    server_rds = _connect_redis()
    devices = server_rds.get('DeviceStatusInfo')
    try:
        from_response['values'] = devices.decode("utf-8")
    except Exception as errors:
        time.sleep(4)
        _logger.error(f'\n an error will  be occured when connecting to redis: {errors}\n')
        from_response['status'] = 404
    return from_response


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    device_id = fields.Char()
    marker_color = fields.Char('Color')

    @api.model
    def get_latlong(self):
        to_utf = depackage_utf_status()
        if to_utf['status'] == 200:
            DeviceStatusInfo = to_utf['values']
        else:
            return to_utf
        info = ast.literal_eval(DeviceStatusInfo)
        for coordonate in info:
            fleet_vehicle_id = self.env['fleet.vehicle'].search([('device_id', '=', coordonate['deviceid'])])
            if len(fleet_vehicle_id) == 1:
                fleet_vehicle_id.driver_id.write({
                    'partner_longitude': coordonate['longitude'],
                    'partner_latitude': coordonate['latitude']
                })
        return True

    @api.model
    def getdevicestatusinfo(self):
        to_utf = depackage_utf_status()
        if to_utf['status'] == 200:
            DeviceStatusInfo = to_utf['values']
        else:
            return to_utf
        info = ast.literal_eval(DeviceStatusInfo)
        for coordonate in info:
            fleet_vehicle_id = self.env['fleet.vehicle'].search([('device_id', '=', coordonate['deviceid'])])
            if len(fleet_vehicle_id) == 1:
                fleet_vehicle_id.driver_id.write({
                    'partner_longitude': coordonate['longitude'],
                    'partner_latitude': coordonate['latitude']
                })

        return info

    @api.model
    def get_partner_coordinate(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id).exists()
        if partner_id:
            return dict(
                partner_latitude=partner.partner_latitude,
                partner_longitude=partner.partner_longitude
            )
        return None
