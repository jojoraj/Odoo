# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'res.partner'
    
    has_Cholera = fields.Boolean( default=True)
    # Job = fields.Char()
    # has_Cholera = fields.Boolean(compute='_compute_has_cholera', store=True, default=True)
    
    # @api.depends('category_id')
    # def _compute_has_cholera(self):
    #     for contract in self:
    #         if 2 not in contract.category_id.ids:
    #             contract.has_Cholera = False