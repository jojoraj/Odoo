# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'res.partner'
    
    Job = fields.Char()
