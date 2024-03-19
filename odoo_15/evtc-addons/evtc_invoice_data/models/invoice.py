from odoo import fields, models


def get_zone(rec, zone):
    order = rec.pos_order_ids.lines.mapped('sale_order_origin_id')
    if order:
        return ', '.join([str(x) for x in order.mapped(zone)])
    return ''


def order_origin(rec):
    order_ids = rec.pos_order_ids.lines.mapped('sale_order_origin_id')
    return order_ids[-1] if len(order_ids) > 1 else order_ids


def get_fields_dicts(rec, fields):
    order = order_origin(rec)
    return order[fields] if order else None


class Invoice(models.Model):
    _inherit = 'account.move'

    # required fields
    pickup_datetime = fields.Datetime(string='Date of recovery', compute='_compute_pickup_datetime')
    role_id = fields.Many2one('planning.role', string='role', compute='_compute_role_id')
    pickup_zone = fields.Char(string='recovery area', compute='_compute_pickup_zone')
    destination_zone = fields.Char(string='destination zone', compute='_compute_destination_zone')
    duration = fields.Float(compute='_compute_duration')
    order_start_date = fields.Datetime(string="start date", compute='_compute_order_start_date',
                                       store=True)
    odometre_start = fields.Float(string="Begin Odometer", compute='_compute_odometre_start')
    position_start = fields.Char(string="Begin coordinate", compute='_compute_position_start')
    destination_datetime = fields.Datetime(string="end data/time", compute='_compute_destination_datetime',
                                           store=True)
    real_duration = fields.Float(string="Course duration", compute='_compute_real_duration')
    odometer_stop = fields.Float(string="Odometer end", compute='_compute_odometer_stop')
    real_distance = fields.Float(string="distance", compute='_compute_real_distance')
    real_cost = fields.Float(string="Cost", compute='_compute_real_cost')
    position_stop = fields.Char(string="end coordinate", compute='_compute_position_stop')

    is_compute_data = fields.Boolean(compute='_compute_is_compute_data')

    def _compute_is_compute_data(self):
        for rec in self:
            rec.is_compute_data = True

    def _compute_pickup_datetime(self):
        for rec in self:
            rec.pickup_datetime = get_fields_dicts(rec, 'pick_up_datetime')

    def _compute_role_id(self):
        for rec in self:
            values = get_fields_dicts(rec, 'role_id')
            rec.role_id = values.id if values else False

    def _compute_pickup_zone(self):
        for rec in self:
            rec.pickup_zone = get_zone(rec, 'pick_up_zone')

    def _compute_destination_zone(self):
        for rec in self:
            rec.destination_zone = get_zone(rec, 'destination_zone')

    def _compute_duration(self):
        for rec in self:
            rec.duration = get_fields_dicts(rec, 'duration')

    def _compute_order_start_date(self):
        for rec in self:
            rec.order_start_date = get_fields_dicts(rec, 'order_start_date')

    def _compute_odometre_start(self):
        for rec in self:
            rec.odometre_start = get_fields_dicts(rec, 'odometer_start')

    def _compute_position_start(self):
        for rec in self:
            rec.position_start = get_fields_dicts(rec, 'position_start')

    def _compute_destination_datetime(self):
        for rec in self:
            rec.destination_datetime = get_fields_dicts(rec, 'order_stop_date')

    def _compute_real_duration(self):
        for rec in self:
            rec.real_duration = get_fields_dicts(rec, 'real_duration')

    def _compute_odometer_stop(self):
        for rec in self:
            rec.odometer_stop = get_fields_dicts(rec, 'odometer_stop')

    def _compute_real_distance(self):
        for rec in self:
            kilometers = get_fields_dicts(rec, 'real_distance')
            if not kilometers:
                move_line_ids = self.env['account.move.line'].search([('move_id', '=', rec.id)])
                line_ids = move_line_ids.filtered(lambda invoice_line: invoice_line.product_uom_id.name in ['Km', 'km'])
                kilometers = line_ids.quantity if len(line_ids) == 1 else sum(
                    line.quantity for line in line_ids if line)
            rec.real_distance = kilometers

    def _compute_real_cost(self):
        for rec in self:
            rec.real_cost = get_fields_dicts(rec, 'real_cost')

    def _compute_position_stop(self):
        for rec in self:
            rec.position_stop = get_fields_dicts(rec, 'position_stop')
