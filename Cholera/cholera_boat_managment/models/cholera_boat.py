# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class CholeraBoat(models.Model):
    _inherit = "fleet.vehicle"

    is_boat = fields.Char(string="Est un bateau")
