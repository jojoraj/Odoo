# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _name = 'boat.type'

    name = fields.Char(string='Type de bateau')
