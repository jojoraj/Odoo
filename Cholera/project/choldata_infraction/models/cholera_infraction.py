# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Infraction(models.Model):
    """
    Model representing infractions.
    """
    _name = 'cholera.infraction'
    _description = 'Infraction'
    _inherit = ['mail.thread']

    name = fields.Char('Infraction', required=True)
    comment = fields.Text('Comments')
    individu_type = fields.Selection(
        [('vehicle', "Vehicle"), ('patient', "Patient"), ('others', "Others")],
        string="Individu Type", default='vehicle',
    )
    type_id = fields.Many2one('infraction.type', string='Type')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    partner_id = fields.Many2one('res.partner', string='Patient')

    # @api.onchange('individu_type')
    # def _onchange_individu_type(self):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }

    @api.constrains('vehicle_id')
    def _check_vehicle_required(self):
        for record in self:
            if record.individu_type == 'vehicle' and not record.vehicle_id:
                raise ValidationError("Le véhicule est obligatoire.")

    @api.constrains('partner_id')
    def _check_partner_required(self):
        for record in self:
            if record.individu_type == 'patient' and not record.partner_id:
                raise ValidationError("Le patient est obligatoire.")


class InfractionType(models.Model):
    """
    Model representing types of infractions.
    """
    _name = 'infraction.type'
    _description = 'Infraction Type'
    _rec_name = 'type'

    type = fields.Char('Infraction Type', required=True)
