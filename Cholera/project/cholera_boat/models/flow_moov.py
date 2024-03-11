# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class FlowMoov(models.Model):
    _name = 'flow.moov'
    _rec_name = 'fleet_vehicle_id'

    origin_id = fields.Many2one(comodel_name='destination.vehicle', string='Origine', required=True)
    destination_id = fields.Many2one(comodel_name='destination.vehicle', string='Destination', required=True)
    merchandise_type = fields.Char(string='Merchendise type')
    total_passenger = fields.Integer(string="Total passengers", compute="count_passenger")

    passenger_ids = fields.Many2many(
        'res.partner', string='Passenger', groups="base.group_user")

    boat_type_flow = fields.Char(string="Boat type", compute='_compute_boat_type_flow')

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', required=True)

    time = fields.Datetime(default=lambda self: datetime.now(), required=True)

    sanitary_barrier_id = fields.Many2one('sanitary.barrier')

    def count_passenger(self):
        self.total_passenger = len(self.passenger_ids)

    @api.depends('fleet_vehicle_id.boat_type')
    def _compute_boat_type_flow(self):
        for record in self:
            record.boat_type_flow = record.fleet_vehicle_id.boat_type.name
