# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
class CrmStageTwo(models.Model):
    
    _name = 'crm.global.stage'
    _description = 'Étapes globales des CRM'
    _order = "sequence, name, id"

    active = fields.Boolean(default=True)
    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1)
    on_change = fields.Boolean('Change Probability Automatically' )
    fold = fields.Boolean('Folded in Pipeline' )
    team_id = fields.Many2one('crm.team', string='Sales Team', ondelete='set null',
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    team_count = fields.Integer('team_count', compute='_compute_team_count')

    @api.multi
    def _compute_team_count(self):
        for stage in self:
            stage.team_count = self.env['crm.team'].search_count([])   