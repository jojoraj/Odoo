
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'pos.session'

    def get_geolocalization_type(self, role_id):
        role_id = self.env['planning.role'].browse(role_id.get('id'))
        if role_id:
            vehicle_id = role_id.vehicle_id
            if vehicle_id.geolocalization_type:
                return vehicle_id.geolocalization_type
            else:
                return ""

   