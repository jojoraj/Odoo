##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pick_up_datetime = fields.Datetime("Pick up date and time")
    # TO DO: Geotab
    pick_up_zone = fields.Text("Exact location")
    pick_up_zone_id = fields.Many2one("res.district", 'Pick up zone')
    # TO DO: Geotab
    destination_zone = fields.Text("Exact location")
    destination_zone_id = fields.Many2one("res.district", 'Destination Zone')
    duration = fields.Float()
    estimated_kilometers = fields.Float()
    client_note = fields.Text("Client notes")
    role_id = fields.Many2one('planning.role', string="Role")
    reference_code = fields.Char()
    payment_method_note = fields.Char()

    def action_confirm(self):
        if self.role_id and self._context.get('from_sale', False):
            return {
                'name': _('Assignment'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'resource.assign.wizard',
                'target': 'new',
            }
        else:
            return super(SaleOrder, self).action_confirm()
