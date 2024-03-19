# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import config

class FleetVehicleState(models.Model):
    _inherit = 'fleet.vehicle.state'

    is_broken_down = fields.Boolean("Indisponible")
    middle_office_value = fields.Selection([
        ('AVAILABLE','AVAILABLE'),
        ('UNAVAILABLE','UNAVAILABLE')
    ], string="Middle Office State", default="AVAILABLE")


    @api.onchange('is_broken_down')
    def _onchange_is_broken_down(self):
        if self.is_broken_down:
            self.write({
                'middle_office_value': 'UNAVAILABLE'
            })
        else:
            self.write({
                'middle_office_value': 'AVAILABLE'
            })