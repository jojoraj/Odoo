# -*- coding: utf-8 -*-

from odoo import fields, models, _


class CholeraBoatModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    name = fields.Char(string='Nom')
