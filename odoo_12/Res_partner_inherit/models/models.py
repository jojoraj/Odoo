# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    cin_number = fields.Integer(string="Numéro CIN")
    nif_stat = fields.Integer(string="NIF STAT")
