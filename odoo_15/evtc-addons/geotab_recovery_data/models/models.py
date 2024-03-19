from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.addons.services.tools import evtc_service
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_PWD = config.get('redis_password', '')
REDIS_DB = config.get('redis_db', 0)
REDIS_USR = config.get('redis_user', '')


class FleetTripAdd(models.Model):
    _inherit = 'esanandro_geotab.fleet.trip'
    _description = 'Fleet trip'

    partner_internal_working_distance = fields.Float(string='Distance parcourue par le partenaire interne')
    partner_clent_working_distance = fields.Float(string='Distance parcourue par le client')

    @api.model
    def set_working_distance(self):
        min_datetime = datetime(self.date.year, self.date.month, self.date.day)
        max_datetime = datetime(
            self.date.year, self.date.month, self.date.day, 23, 59, 0)
        pos_order_ids = self.env['pos.order'].search(
            [('date_order', '>=', min_datetime), ('date_order', '<=', max_datetime), ('session_id', '!=', False)])
        pos_order_ids_filtered = pos_order_ids.filtered(
            lambda pos_order: pos_order.session_id.config_id and pos_order.session_id.config_id.role_id and pos_order.session_id.config_id.role_id.vehicle_id.id == self.vehicle_id.id)

        if pos_order_ids_filtered:
            working_distance = partner_client = internal_partner = 0.0
            for pos_order in pos_order_ids_filtered:
                pos_line = pos_order.lines.filtered(
                    lambda line: line.product_uom_id and line.product_uom_id.name == 'km')
                if pos_line:
                    partner_links = pos_line.order_id.partner_id.partner_type
                    if partner_links == 'client':
                        partner_client += pos_line[0].qty
                    elif partner_links == 'internal':
                        internal_partner += pos_line[0].qty
                    working_distance += pos_line[0].qty
            self.working_distance = working_distance
            self.partner_clent_working_distance = partner_client
            self.partner_internal_working_distance = internal_partner


class IrConfigParameter(models.TransientModel):
    _inherit = 'res.config.settings'

    recovery_kpi_start_date = fields.Datetime(string='Recovery KPI data start date',
                                              config_parameter='ir_cron.recovery_kpi_start_date')
    recovery_kpi_end_date = fields.Datetime(string='Recovery KPI data end date',
                                            config_parameter='ir_cron.recovery_kpi_end_date', default=fields.Date.today)

    def run_kpi_recovery_data(self):
        all_vehicls = self.env['fleet.vehicle'].sudo().search([('device_id', '!=', False)])
        request_start = self.env['ir.config_parameter'].sudo().get_param(
            'ir_cron.recovery_kpi_start_date', False)
        request_end = self.env['ir.config_parameter'].sudo().get_param(
            'ir_cron.recovery_kpi_end_date', False)
        if not request_start or not request_end or not all_vehicls:
            return
        y, m, d = request_start.split(' ')[0].split('-')
        year, month, day = request_end.split(' ')[0].split('-')
        request_start_to_datetime = datetime(int(y), int(m), int(d))
        request_end_to_datetime = datetime(int(year), int(month), int(day), 23, 59)
        fleet_strip = self.env['esanandro_geotab.fleet.trip'].sudo()
        done_multi_call = self.access_client(
            device_ids=all_vehicls.mapped('device_id'),
            date_from=request_start_to_datetime,
            date_to=request_end_to_datetime
        )
        status_data = fleet_strip._dispatch_status_data(done_multi_call)
        fleet_strip.create_trip(all_vehicls, status_data,
                                request_start, request_end)
        self.tip_working_in_time_request(request_start_to_datetime, request_end_to_datetime)

    def tip_working_in_time_request(self, begin, end):
        records = self.env['esanandro_geotab.fleet.trip'].sudo().search([
            ('date', '>=', begin), ('date', '<=', end)
        ])
        for rec in records:
            working_distance = partner_client = internal_partner = 0.0
            vehicle_id = rec.vehicle_id
            min_datetime = datetime(rec.date.year, rec.date.month, rec.date.day)
            max_datetime = datetime(rec.date.year, rec.date.month, rec.date.day, 23, 59, 0)
            pos_order_ids = self.env['pos.order'].sudo().search([
                ('date_order', '>=', min_datetime), ('date_order', '<=', max_datetime),
                ('session_id.config_id.role_id.vehicle_id', '=', vehicle_id.id),
            ])
            for pos_order in pos_order_ids:
                pos_line = pos_order.lines.filtered(
                    lambda line: line.product_uom_id and line.product_uom_id.name == 'km'
                )
                if pos_line:
                    partner_links = pos_line.order_id.partner_id.partner_type
                    if partner_links == 'client':
                        partner_client += pos_line[0].qty
                    elif partner_links == 'internal':
                        internal_partner += pos_line[0].qty
                    working_distance += pos_line[0].qty
            rec.working_distance = working_distance
            rec.partner_clent_working_distance = partner_client
            rec.partner_internal_working_distance = internal_partner

    def json_object(self, _id, date):
        years, month, day = date.year, date.month, date.day
        # 2022-03-05T00:00:00Z, 2022-03-05T23:59:00Z
        first_time = f"{years}-{month}-{day}T00:00:00Z"
        last_time = f"{years}-{month}-{day}T23:59:00Z"
        request = dict(
            diagnosticSearch=dict(id="DiagnosticOdometerAdjustmentId"),
            deviceSearch=dict(id=_id),
            FromDate=first_time,
            ToDate=last_time
        )
        return request

    def access_client(self, device_ids, date_from, date_to):
        EVTC = evtc_service.EvtcService(REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        request = []
        for _id in device_ids:
            interval_ = date_from
            while interval_ < date_to:
                request += [
                    ('Get', dict(typeName="StatusData", search=self.json_object(_id, interval_)))
                ]
                interval_ += timedelta(days=1)
        status_data = EVTC.recovery_service(request)
        return status_data

    def recompute_all_working_day(self):
        """
            @params: None
            @returns: None
            @method: calculate all vehicle daily working
        """
        odometer = self.env['fleet.vehicle.odometer'].search([]).mapped('vehicle_id').ids
        order_odometer = set(odometer)
        for vehicule_id in order_odometer:
            fleet_ids = self.env['fleet.vehicle.odometer'].search([("vehicle_id", '=', vehicule_id)], order='date')
            lengh_fleet = len(fleet_ids)
            count = 1
            if lengh_fleet > 1:
                while count <= lengh_fleet - 1:
                    now_vals = fleet_ids[count]
                    last_vals = fleet_ids[count - 1]
                    now_vals.working_daily = now_vals.value - last_vals.value
                    count += 1


class DailyWorking(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    working_daily = fields.Float(string='Daily Working')


class CronDailyWorking(models.Model):
    _inherit = 'esanandro_geotab.fleet.trip'
    _description = "add daily working in cron data"

    @api.model
    def create_odometer(self, status_date, vehicle, value):
        """
            @params: status_date, vehicle, value
            @method: compute vechicle daily working for vehicle

        """
        response = super(CronDailyWorking, self).create_odometer(status_date, vehicle, value)
        domain = [('vehicle_id', '=', vehicle.id)]
        odometer = self.env['fleet.vehicle.odometer'].search(domain, order='date DESC')
        if odometer and len(odometer) >= 2:
            before_last = odometer[1]
            last_odometer = odometer[0]
            last_odometer.working_daily = last_odometer.value - before_last.value
        return response
