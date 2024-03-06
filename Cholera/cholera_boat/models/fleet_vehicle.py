# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    passenger_number = fields.Integer(string='Nombre de passagers entrants')
    merchandise_type = fields.Char(string='Type de marchandise')

    test = fields.Char(string='Champ a cacher')

    crew = fields.Char(string="Nom")
    native_country = fields.Many2one(comodel_name='res.country', string="Pays d'origine")
    nationality = fields.Char(string="Nationalité")
    tel_number = fields.Char(string="Numéro de téléphone")
    mail_address = fields.Char(string="Adresse mail")
    is_boat = fields.Boolean(string="Est un bateau")
    is_double = fields.Boolean()
    flux = fields.Char(string="Flux")

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
                'view_mode': 'form',
                'res_model': 'flow.moov',
                'type': 'ir.actions.act_window',
                'domain': [('fleet_vehicle_id', '=', self.id)],
                'context': {
                    'default_fleet_vehicle_id': self.id,
                    'create': False
                }
            }

        res_model = self.env['flow.moov'].search([('fleet_vehicle_id', '=', self.id)], limit=1)
        if res_model:
            action['res_id'] = res_model.id
        return action
