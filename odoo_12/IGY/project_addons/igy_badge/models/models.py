# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IGY_Badge(models.Model):
    _name = 'igy.badge'
    _description = 'Changement de badge IGY'

    name = fields.Char(string="Nom", required=True)

# class igy_badge(models.Model):
#     _name = 'igy_badge.igy_badge'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100