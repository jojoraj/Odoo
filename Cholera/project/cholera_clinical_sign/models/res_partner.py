# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class HrContract(models.Model):
    _inherit = 'res.partner'
    
    
    disease_start_date = fields.Date()
    watery_diarrhea = fields.Boolean()
    nausea = fields.Boolean()
    vaumissement = fields.Boolean()
    leg_cramp = fields.Boolean()
    dehydration = fields.Boolean()