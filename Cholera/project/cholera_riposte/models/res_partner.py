# -*- coding: utf-8 -*-

from odoo import models, fields, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_chemo = fields.Boolean(string="Ayant bénéficier du chimioprophylaxie")
    sanitary_training = fields.Many2one(comodel_name='sanitary.training', string='Formation sanitaire')
    water_source = fields.Many2one(comodel_name='water.source', string='Source de consommation')
    other_source = fields.Text(string='Autres sources à préciser')

    def action_test(self):
        action = {
                'name': _('Riposte'),
                'view_mode': 'form',
                'res_model': 'cholera.riposte',
                'type': 'ir.actions.act_window',
                'domain': [('partner_id', '=', self.id)],
                'context': {
                    'default_partner_id': self.id,
                    'create': False
                }
            }

        res_model = self.env['cholera.riposte'].search([('partner_id', '=', self.id)], limit=1)
        if res_model:
            action['res_id'] = res_model.id
        return action
