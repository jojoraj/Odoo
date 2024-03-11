# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class ResPartner(models.Model):
    """
    Model representing Partner.
    """
    _inherit = 'res.partner'

    @api.multi
    def _compute_infraction_partner_count(self):
        for partner in self:
            partner.infraction_partner_count = self.env['cholera.infraction'].search_count([('partner_id', '=', partner.id)])

    infraction_partner_count = fields.Integer('Infractions', compute='_compute_infraction_partner_count')

    def action_infraction_partner(self):
        action = {
            'name': _('Infraction(s)'),
            'view_mode': 'tree,form',
            'res_model': 'cholera.infraction',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'create': False
            }
        }
        res_model = self.env['cholera.infraction'].search([('partner_id', '=', self.id)], limit=1)
        action['res_id'] = res_model.id if res_model else False
        return action
