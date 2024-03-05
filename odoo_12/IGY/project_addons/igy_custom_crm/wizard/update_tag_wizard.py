# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class UpdateTag(models.TransientModel):
    _name = 'update.tag'

    lead_ids = fields.Many2many('crm.lead', string=_("Pipeline"))
    crm_lead_tag_ids = fields.Many2many('crm.lead.tag', string=_("Étiquettes"))

    @api.multi
    def update_tag(self):
        """Method to update multiple lead tags"""
        for line in self:
            list(map(lambda lead: lead.update({
                'tag_ids': [(6, 0, line.crm_lead_tag_ids.mapped('id'))]
            }), line.lead_ids))
