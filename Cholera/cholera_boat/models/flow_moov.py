# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class FlowMoov(models.Model):
    _name = 'flow.moov'
    _rec_name = 'fleet_vehicle_id'

    origin = fields.Many2one(comodel_name='res.country', string='Origine')
    destination = fields.Many2one(comodel_name='res.country', string='Déstination')

    total_passenger = fields.Integer(string="Total passagers", compute="count_passenger")
    origin = fields.Many2one(comodel_name='res.country', string='Origine')
    destination = fields.Many2one(comodel_name='res.country', string='Déstination')

    passenger_ids = fields.Many2many(
        'res.partner', string='Passenger', groups="base.group_user")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', required=True)
    moov = fields.Selection([
        ('enter', 'Enter'),
        ('exit', 'Exit'),
        ])
    time = fields.Datetime(default=lambda self: datetime.now(), required=True)

    sanitary_barrier_id = fields.Many2one('sanitary.barrier')

    def count_passenger(self):
        self.total_passenger = len(self.passenger_ids)
