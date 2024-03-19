import logging
import time
from datetime import datetime

from odoo import fields, models
from odoo.addons.services.tools import evtc_service
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_DB = config.get('redis_db', 0)
REDIS_PWD = config.get('redis_password', '')
REDIS_USR = config.get('redis_user', '')
_logger = logging.Logger(__name__)


class SaleOrderReser(models.Model):
    _inherit = "sale.order"
    _description = 'Reservation for geotab'

    reservation_status = fields.Boolean(default=False, store=True)
    order_start_date = fields.Datetime(string="Date/Heure debut course", tracking=True)
    order_stop_date = fields.Datetime(string="Date/Heure fin course", tracking=True)
    real_duration = fields.Float(string="Duration course", tracking=True)
    odometer_start = fields.Float(string="Odomètre Debut course", tracking=True)
    odometer_stop = fields.Float(string="Odomètre Fin course", tracking=True)
    real_distance = fields.Float(string="Distance parcourue", tracking=True)
    position_start = fields.Char(string="Coordonnées debut course", tracking=True)
    position_stop = fields.Char(string="Coordonnées Fin course", tracking=True)
    real_cost = fields.Float(string="Cout finale", tracking=True)

    def stop_iteration(self, *args, **kwargs):
        try:
            order = kwargs.get('order')
            price_unit = kwargs.get('price_unit')
            role_id = kwargs.get('role_id')
            # order.real_duration = order.order_start_date - datetime.now()
            if order:
                order_id = int(order.get('id'))
                self = self.browse(order_id)
                self.reservation_status = not self.reservation_status
                diff = self.order_start_date - datetime.now()
                self.real_duration = diff.seconds / 60
                redis_evtc = evtc_service.EvtcService(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
                if role_id:
                    role_id = self.env['planning.role'].browse(role_id[0])
                    device_id = role_id.vehicle_id.device_id
                    infos = redis_evtc.get_info_stop(order_id, device_id)

                    if infos:
                        self.real_duration = infos.get("duration")
                        self.real_distance = infos.get("distance")
                        self.real_cost = round(infos.get("distance"), 2) * price_unit
                        self.odometer_stop = float(float(infos.get('odometer'))) / 1000
                        value = infos.get('position')
                        self.position_stop = f"{value['x']}, {value['y']}"
                        return {"distance": infos.get("distance")}

            return self.reservation_status
        except Exception as e:
            _logger.error(e)

    def get_done_distance(self, *args, **kwargs):
        try:
            order = kwargs.get('order')
            role_id = kwargs.get('role_id')
            # order.order_start_date = datetime.now()
            if role_id:
                role_id = self.env['planning.role'].browse(role_id[0])
                device_id = role_id.vehicle_id.device_id
                if order and device_id:
                    stage_id = self.env.ref('crm.stage_lead3').id
                    order_id = int(order.get('id'))
                    self = self.browse(order_id)
                    self.opportunity_id.stage_id = stage_id
                    self.order_start_date = datetime.now()
                    time.sleep(5)
                    if not self.reservation_status:
                        # order = kwargs.get('order')
                        # timezone = self.env.user.tz
                        # timezone = pytz.timezone(timezone).utcoffset(datetime.now())

                        redis_evtc = evtc_service.EvtcService(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
                        orders = redis_evtc.get_info_start(order_id, device_id)

                        if orders[0]:
                            # self.order_start_date = datetime.strptime(orders[1].get('datetime_1'), "%Y-%m-%dT%H:%M:%SZ")
                            self.odometer_start = float(orders[1].get('odometer_1')) / 1000
                            value = orders[1].get('position_1')
                            self.position_start = f"{value['x']}, {value['y']}"
                        distance = redis_evtc.get_distance_order(order_id) or 0

                        return {"distance": distance}

            return False
        except Exception as e:
            _logger.error(e)

    def get_destination(self, *args, **kwargs):
        r = evtc_service.EvtcService(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        DeviceStatusInfo = r.get_device_status_info()
        try:
            order = kwargs.get('order')
            if order:
                order_id = int(order.get('id'))
                self = self.browse(order_id)
                deviceid = self.role_id.vehicle_id.device_id
                device_info = list(filter(lambda device: device['deviceid'] == deviceid, DeviceStatusInfo))
                destination_latitude = self.opportunity_id.dest_lat
                destination_longitude = self.opportunity_id.dest_long
                pick_lat = self.opportunity_id.pick_up_lat
                pick_long = self.opportunity_id.pick_up_long
                if destination_latitude and destination_longitude:
                    return {'latitude': device_info[0]['latitude'],
                            'longitude': device_info[0]['longitude'],
                            'pick_lat': pick_lat,
                            'pick_long': pick_long,
                            'dest_lat': destination_latitude,
                            'dest_long': destination_longitude}
                else:
                    return False
            else:
                return False
        except Exception as e:
            _logger.error(e)
