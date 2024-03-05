# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
class CrmStage(models.Model):
    
    _inherit = 'crm.stage'
    _description = 'Étape dans le Workflow du CRM '

    active = fields.Boolean(default=True)

    @api.model
    def update_won_active(self):
        won_stage_data_id = self.env.ref('crm.stage_lead4').id
        won_stage_id = self.sudo().browse(won_stage_data_id)
        won_stage_id.update({
            'active': False,
            'sequence': 200
        })
