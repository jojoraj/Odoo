# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class UpdateStage(models.TransientModel):
    _name = 'update.stage'

    lead_ids = fields.Many2many('crm.lead', string=_("Pipelines"))
    crm_stage_id = fields.Many2one('crm.stage', string=_("Etape"))

    @api.multi
    def update_stage(self):
        """Method to update multiple lead stage"""
        for line in self:
            list(map(lambda lead: lead.update({
                'stage_id': line.crm_stage_id.id
            }), line.lead_ids))
