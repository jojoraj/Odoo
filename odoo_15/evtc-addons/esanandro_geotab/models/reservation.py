import logging

from mygeotab.exceptions import MyGeotabException
from odoo import _, api, fields, models
from odoo.addons.services.tools import evtc_service
from odoo.exceptions import MissingError
from odoo.tools import config

_logger = logging.getLogger(__name__)

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_DB = config.get('redis_db', 0)
REDIS_PWD = config.get('redis_password', '')
REDIS_USR = config.get('redis_user', '')


class Reservation(models.Model):
    _name = 'esanandro_geotab.reservation'
    _description = 'e-vtc reservation'

    # tariff_plan_id = fields.Many2one(comodel_name='esanandro_geotab.tariff.plan',
    #                                  string='Tarrif plan', required=True)
    # price_per_km = fields.Float(
    #     related='tariff_plan_id.list_price', string='Price/km', readonly=True)

    state = fields.Selection([('waiting', 'Waiting'), ('in_progress', 'In progress'),
                              ('done', 'Done'), ('cancelled', 'Cancelled')], default='waiting', required=True)
    pick_up_point = fields.Char(string='Pick-up point', required=True)
    put_back_point = fields.Char(string='Put-back point', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner')
    mobile_to_contact = fields.Char()
    date_from = fields.Datetime(default=fields.Datetime.now(), required=True)
    date_to = fields.Datetime(readonly=True)

    distance = fields.Float(string="Distance(km)",
                            compute="_compute_distance_duration", readonly=True,
                            compute_sudo=True, store=True)
    duration = fields.Char(readonly=True, compute="_compute_distance_duration")
    total_price = fields.Float(readonly=True, compute="_compute_total_price")

    fleet_vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle', string='Vehicle')

    cancellation_reason = fields.Text()

    @api.onchange('tariff_plan_id')
    def _get_fleet_vehicle_domain(self):
        return {
            'domain': {
                'fleet_vehicle_id': [
                    ('id', 'in', self.tariff_plan_id.fleet_vehicle_ids.mapped('id'))
                ]
            }
        }

    @api.onchange('duration', 'distance')
    def _compute_total_price(self):
        for reservation in self:
            if reservation.distance:
                reservation.total_price = round(
                    reservation.price_per_km, 2) * round(reservation.distance, 2)
            else:
                reservation.total_price = 0.0

    @api.onchange('pick_up_point', 'put_back_point')
    def _compute_distance_duration(self):
        evtc_serv = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        for reservation in self:
            if reservation.pick_up_point and reservation.put_back_point:
                address_points = [reservation.pick_up_point,
                                  reservation.put_back_point]
                addresses = evtc_serv.get_coordinates(address_points)
                way_points = []
                for index, address in enumerate(addresses):
                    if address:
                        way_points.append({
                            'coordinate': {
                                'x': address['x'],
                                'y': address['y'],
                            },
                            'sequence': index,
                            'description': address_points[index]
                        })
                    else:
                        raise MissingError(
                            _('Localization not found - {}.').format(address_points[index]))
                try:
                    directions = evtc_serv.get_directions(way_points)
                    if directions and directions['legs'] and len(directions['legs']) > 0:
                        leg = directions['legs'][0]
                        reservation.distance = leg['distance']
                        reservation.duration = leg['duration']
                except MyGeotabException as ex:
                    raise MissingError(_(f'Could not get directions from these points with this error {str(ex)}.')) from ex

    @api.model
    def create(self, values):
        new_reservation = super(Reservation, self).create(values)
        return new_reservation

    @api.onchange('partner_id')
    def _onchange_partner(self):
        for reservation in self:
            if not reservation.mobile_to_contact and reservation.partner_id:
                reservation.mobile_to_contact = reservation.partner_id.mobile

    def name_get(self):
        res = []
        for reservation in self:
            res.append(
                (reservation.id, _("Reservation,{}").format(reservation.id)))
        return res

    def btn_go_click(self):
        self.state = 'in_progress'
        self.env['sale.order'].create(
            {
                'partner_id': self.partner_id.id,
                'date_order': self.date_from,
                'reservation_id': self.id,
                'order_line': [(0, 0, {
                    'name': self.tariff_plan_id.product_template_id.name,
                    'product_id': self.tariff_plan_id.product_template_id.id,
                    'product_uom': self.tariff_plan_id.product_template_id.uom_po_id.id,
                    'product_uom_qty': self.distance,
                    'price_unit': self.tariff_plan_id.product_template_id.list_price,
                }), (0, 0, {
                    'display_type': 'line_note',
                    'name': _('Pick up zone: %s - Destination zone: %s') % (
                        self.pick_up_point, self.put_back_point,
                    )})]
            }
        )

    def btn_done_click(self):
        self.state = 'done'

    def get_reservation_information(self, pickup_point, storage_point):
        if not pickup_point and not storage_point:
            return
        result = list()
        point = [pickup_point, storage_point]
        # connect to redis
        redis_evtc = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        # get x,y (coordinate) of point
        adress = redis_evtc.get_coordinates(point)
        # {'coordinate': {'x': 47.507904052734375, 'y': -18.87919044494629}, 'sequence': 1, 'description': 'antananarivok'}
        for index, address in enumerate(adress):
            if address:
                result.append({'coordinate': {'x': address['x'], 'y': address['y'], 'description': point[index]}})
        try:
            if result:
                directions = redis_evtc.get_directions(result)
                if directions and directions['legs'] and len(directions['legs']) > 0:
                    leg = directions['legs'][0]
                    return [result, [leg['distance'], leg['duration']]]
        except MyGeotabException as e:
            _logger.error(str(e))

    @api.model
    def get_all_vehicle_on_tarif(self, tarif):
        # params:
        # return ['veicule']
        tarif_plan = self.env['esanandro_geotab.tariff.plan'].browse(int(tarif))
        vehicle = self.env['fleet.vehicle'].search([
            ('id', 'in', tarif_plan.fleet_vehicle_ids.mapped('id'))
        ])
        results = [{
            'name': rec.name,
            'fleet_id': rec.id,
            'seat': rec.seats,
            'color': rec.color,
            'driver': rec.driver_id.name} for rec in vehicle]

        return results

    def get_point_lat_long(self, address):
        result = list()
        if not address:
            return result
        redis_evtc = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)

        adress = redis_evtc.get_coordinates([address])
        # {'coordinate': {'x': 47.507904052734375, 'y': -18.87919044494629}, 'sequence': 1, 'description': 'antananarivok'}
        for _index, address in enumerate(adress):
            if address:
                result.append({'x': address['x'], 'y': address['y']})
        return result

    def get_models_way_point(self, address):
        if not address:
            return []
        # connect to redis
        result = []
        redis_evtc = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        # get x,y (coordinate) of point
        adress = redis_evtc.get_coordinates(address)
        # {'coordinate': {'x': 47.507904052734375, 'y': -18.87919044494629}, 'sequence': 1, 'description': 'antananarivok'}
        for _index, address in enumerate(adress):
            if address:
                result.append({
                    'coordinate': {'x': address['x'], 'y': address['y']}
                })
        try:
            if result:
                directions = redis_evtc.get_directions(result)
                if directions and directions['legs'] and len(directions['legs']) > 0:
                    leg = directions['legs'][0]
                    return [result, [leg['distance'], leg['duration']]]
        except MyGeotabException as e:
            _logger.error(e)

        sale_orders = self.env['sale.order'].search([
            ('reservation_id', '=', self.id)
        ])
        for sale_order in sale_orders:
            sale_order.state = 'sale'

    # get adress with lat and long
    def get_new_adress_with_latLng(self, coordinate):
        lat = coordinate.get('lat')
        lng = coordinate.get('lng')
        conn_redis = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR)
        return conn_redis.get_address(x=lng, y=lat)
