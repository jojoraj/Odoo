# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    boat_type = fields.Many2one('boat.type', string="Type de bateau")
    crew = fields.Many2one('res.partner', string="Nom")
    crew_ids = fields.Many2many('res.partner', string='Equipages', groups="base.group_user")
    native_country = fields.Many2one(comodel_name='res.country', string="Pays d'origine")
    nationality = fields.Char(string="Nationalité")
    tel_number = fields.Char(string="Numéro de téléphone")
    mail_address = fields.Char(string="Adresse mail")
    is_boat = fields.Boolean(string="Est un bateau")
    is_double = fields.Boolean()
    flux_count = fields.Integer('Flux', compute='_compute_flux_count')

    @api.multi
    def _compute_flux_count(self):
        for rec in self:
            rec.flux_count = self.env['flow.moov'].search_count([('fleet_vehicle_id', '=', rec.id)])

    @api.onchange('tag_ids')
    def hide_field(self):
        for rec in self:
            vehicle = rec.tag_ids.mapped('name')

            if len(vehicle) == 1:
                rec.is_double = False
                if 'Bateau' in vehicle:
                    rec.is_boat = True
                else:
                    rec.is_boat = False
            elif len(vehicle) > 1:
                raise UserError(_('Veuillez selectionner un seul vehicule'))
                rec.is_double = True
                rec.is_boat = False
            else:
                rec.is_boat = False

    def flux_action(self):
        action = {
            'name': _('Flux'),
            'view_mode': 'tree,form',
            'res_model': 'flow.moov',
            'type': 'ir.actions.act_window',
            'domain': [('fleet_vehicle_id', '=', self.id)],
            'context': {
                'default_fleet_vehicle_id': self.id,
                'create': True
            }
        }

        res_model = self.env['flow.moov'].search([('fleet_vehicle_id', '=', self.id)], limit=1)
        if res_model:
            action['res_id'] = res_model.id
        return action
