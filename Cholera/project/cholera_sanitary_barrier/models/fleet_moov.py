# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class FleetMoov(models.Model):
    _name = 'fleet.moov'
    
    passenger_ids = fields.Many2many(
        'res.partner', string='Passenger', groups="base.group_user")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', required = True)
    moov = fields.Selection([
        ('enter', 'Enter'),
        ('exit', 'Exit'),
        ])
    time = fields.Datetime(default=lambda self: datetime.now(), required = True)
    
    sanitary_barrier_id = fields.Many2one('sanitary.barrier', required = True)
