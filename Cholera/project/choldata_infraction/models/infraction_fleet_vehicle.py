# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class FleetVehicle(models.Model):
    """
    Model representing Vehicle.
    """
    _inherit = 'fleet.vehicle'

    @api.multi
    def _compute_infraction_vehicle_count(self):
        for vehicle in self:
            vehicle.infraction_vehicle_count = self.env['cholera.infraction'].search_count([('vehicle_id', '=', vehicle.id)])

    infraction_vehicle_count = fields.Integer('Infractions', compute='_compute_infraction_vehicle_count')

    def action_infraction_vehicle(self):
        action = {
            'name': _('Infraction(s)'),
            'view_mode': 'tree,form',
            'res_model': 'cholera.infraction',
            'type': 'ir.actions.act_window',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {
                'default_vehicle_id': self.id,
                'create': False
            }
        }
        res_model = self.env['cholera.infraction'].search([('vehicle_id', '=', self.id)], limit=1)
        action['res_id'] = res_model.id if res_model else False
        return action
