from datetime import datetime
from datetime import time

from odoo import _, api, fields, models
from odoo.addons.services.tools import evtc_service
from odoo.exceptions import MissingError
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_PWD = config.get('redis_password', '')
REDIS_DB = config.get('redis_db', 0)
REDIS_USR = config.get('redis_user', '')


class FleetTrip(models.Model):
    _name = 'esanandro_geotab.fleet.trip'
    _description = 'Fleet trip'

    distance = fields.Float(string="Distance parcourue")
    working_distance = fields.Float(string="Distance parcourue avec client")
    date = fields.Date()
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle')

    @api.model
    def _dispatch_status_data(self, status_data):
        output = {}
        for data in status_data:
            for status in data:
                if status['device']['id'] not in output:
                    output[status['device']['id']] = {}
                if status['dateTime'].date() not in output[status['device']['id']]:
                    output[status['device']['id']][status['dateTime'].date()] = [status]
                else:
                    output[status['device']['id']][status['dateTime'].date()].append(status)

        return output

    @api.model
    def _update_trip(self):

        server_requests = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR
        )
        vehicle_ids = self.env['fleet.vehicle'].search([('device_id', '!=', False)])
        if not vehicle_ids:
            raise MissingError(_('No vehicle found!'))
        request_date = fields.Date.today()
        end_time = time(23, 59)
        request_end = datetime.combine(request_date, end_time)

        status_data = self._dispatch_status_data(
            server_requests.get_done_distance_multi_call(
                device_ids=vehicle_ids.mapped('device_id'),
                date_from=request_date,
                date_to=request_end
            )
        )
        self.create_trip(vehicle_ids, status_data, request_date, request_end)

    @api.model
    def _get_device_id(self, status_data):
        for date_key in status_data:
            for status in status_data[date_key]:
                return status['device']['id']
        return None

    @api.model
    def create_trip(self, vehicle_ids, status_data, request_start, request_end):
        for status in status_data:
            vehicle = vehicle_ids.filtered(
                lambda vehicle: vehicle.device_id == self._get_device_id(status_data[status]))
            if vehicle:
                for status_date in status_data[status]:
                    if not self._is_trip_exists(vehicle.id, status_date):
                        strip = 0
                        if len(status_data[status][status_date]) > 1:
                            strip += abs(
                                status_data[status][status_date][-1]['data'] - status_data[status][status_date][0][
                                    'data'])
                        else:
                            strip += abs(status_data[status][status_date][0]['data']) / 1000
                        trip_id = self.env['esanandro_geotab.fleet.trip'].sudo().create({
                            'distance': strip,
                            'date': status_date,
                            'vehicle_id': vehicle.id,
                        })
                        trip_id.set_working_distance()
                        odometer = status_data[status][status_date][-1]['data'] / 1000
                        self.create_odometer(status_date, vehicle, odometer)

    @api.model
    def create_odometer(self, status_date, vehicle, value):
        odometer = self.env['fleet.vehicle.odometer']
        odometer.create({
            'date': status_date,
            'vehicle_id': vehicle.id,
            'driver_id': vehicle.driver_id.id,
            'value': value
        })

    @api.model
    def set_working_distance(self):
        min_datetime = datetime(self.date.year, self.date.month, self.date.day)
        max_datetime = datetime(
            self.date.year, self.date.month, self.date.day, 23, 59, 0)
        pos_order_ids = self.env['pos.order'].search(
            [('date_order', '>=', min_datetime), ('date_order', '<=', max_datetime), ('session_id', '!=', False)])
        pos_order_ids_filtered = pos_order_ids.filtered(
            lambda
                pos_order: pos_order.session_id.config_id and pos_order.session_id.config_id.role_id and pos_order.session_id.config_id.role_id.vehicle_id.id == self.vehicle_id.id)

        if pos_order_ids_filtered:
            working_distance = 0.0
            for pos_order in pos_order_ids_filtered:
                pos_line = pos_order.lines.filtered(
                    lambda line: line.product_uom_id and line.product_uom_id.name == 'km')

                if pos_line:
                    working_distance += pos_line[0].qty
            self.working_distance = working_distance

    @api.model
    def _is_trip_exists(self, vehicle_id, date):
        return self.env['esanandro_geotab.fleet.trip'].search_count(
            [('vehicle_id', '=', vehicle_id), ('date', '=', date)])
