# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _name = 'destination.vehicle'

    name = fields.Char(string='Destination')
