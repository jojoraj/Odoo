##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 Arkeup (<https://www.etechconsulting-mg.com>). All Rights Reserved
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

from odoo import fields, models


class AssignWizard(models.TransientModel):
    _name = "resource.assign.wizard"
    _description = "Assign Resource Wizard"

    resource_id = fields.Many2one('resource.resource', 'Resource')

    def validate(self):
        """
        Assign Resource
        :rtype: object
        """
        self.ensure_one()

        order_id = self.env['sale.order'].browse(self._context.get('active_id'))

        planning_obj = self.env['planning.slot']
        planning_ids = planning_obj.search([('sale_line_id.order_id', '=', order_id.id)])

        for planning_id in planning_ids:
            planning_id.write({
                'resource_id': self.resource_id.id,
            })
        # Confirm order
        order_id.with_context(from_sale=False).action_confirm()
        # Set state of opportunity to 'in progress'
        if order_id.opportunity_id and order_id.opportunity_id.stage_id.id == self.env.ref('crm.stage_lead2').id:
            order_id.opportunity_id.stage_id = self.env.ref('crm.stage_lead3').id
        return {'type': 'ir.actions.act_window_close'}
