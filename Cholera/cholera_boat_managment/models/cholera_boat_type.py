# -*- coding: utf-8 -*-

from odoo import fields, models, _


class CholeraBoatType(models.Model):
    _name = 'cholera.boat.type'

    name = fields.Char(string='Type de bateau')
