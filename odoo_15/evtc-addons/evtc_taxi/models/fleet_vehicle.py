import json

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    tag_id = fields.Many2one('fleet.vehicle.tag')
    tag_ids = fields.Many2many(readonly=1)

    def write(self, values):
        if values.get('state_id', False) and values.get('driver_id', self.driver_id.id) and not self.env.context.get('from_update_mo', False):
            driver_id = self.env['res.partner'].browse(
                values['driver_id']) if values.get('driver_id', False) else self.driver_id
            if values['state_id'] == self.env.ref('evtc_taxi.blocked').id:
                middle_office_id = self.env['middle.office'].get_default_mo()
                dump_vals = json.dumps({
                    'driverPhone': driver_id.get_formatted_phone(),
                    'status': 'UNFIT'
                })
                middle_office_id.update_vehicle_status(dump_vals)
            blocked_busy = [self.env.ref('evtc_taxi.busy').id, self.env.ref('evtc_taxi.blocked').id]
            if values['state_id'] in blocked_busy:
                driver_id.write({'state_vehicle_id': values['state_id']})
            else:
                driver_id.write({'state_vehicle_id': self.env.ref('evtc_taxi.fleet_vehicle_state_unvailable')})
        return super().write(values)

    @api.model
    def update_vehicle_state_from_mo(self):
        middle_office_id = self.env['middle.office'].get_default_mo()
        vehicle = middle_office_id.get_vehicle_list()
        if vehicle.status_code == 200:
            STATUS_MAPPING = {
                'AVAILABLE': self.env.ref('fleet.fleet_vehicle_state_registered'),
                'UNAVAILABLE': self.env.ref('evtc_taxi.fleet_vehicle_state_unvailable'),
                'BUSY': self.env.ref('evtc_taxi.busy'),
                'UNFIT': self.env.ref('evtc_taxi.blocked'),
            }
            vehicle_json = vehicle.json()
            vehicle_list = vehicle_json['_embedded']['vehicle']
            driver_ids = self.env['res.partner'].search([('external_diver', '=', True)])
            for vehicle_obj in vehicle_list:
                partner_id = driver_ids.filtered(
                    lambda driver: driver.phone and driver.phone.replace(' ', '') == vehicle_obj['driverPhone'])
                if partner_id:
                    vehicle_id = self.search([('driver_id', '=', partner_id.id)])
                    state_id = STATUS_MAPPING.get(vehicle_obj['status'], False)
                    if vehicle_id and state_id:
                        vehicle_id.with_context(from_update_mo=True).write({'state_id': state_id.id})
                        partner_id.write({'state_vehicle_id': state_id.id})
        return vehicle.json()
