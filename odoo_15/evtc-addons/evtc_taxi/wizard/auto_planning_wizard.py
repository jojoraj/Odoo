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
import logging
import time

from odoo import api, fields, models

# Get server timezone
TZ = (time.timezone / 60 / 60) if time.timezone != 0 else -3
MARGIN = 3600
_logger = logging.Logger(__name__)


class AutoPlanningWizard(models.TransientModel):
    _inherit = 'auto.planning.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(AutoPlanningWizard, self).default_get(fields_list)
        filtered_planning = list()
        for planning_data in res['planning_ids']:
            role_id = self.env['planning.role'].browse(planning_data[-1]['role_id'])
            if role_id.vehicle_id.state_id != self.env.ref('evtc_taxi.blocked'):
                filtered_planning.append(planning_data)
        res['planning_ids'] = filtered_planning
        return res

    def update_values(self, slot_id, start_datetime, end_datetime, state):
        res = super(AutoPlanningWizard, self).update_values(slot_id, start_datetime, end_datetime, state)
        res['tag_id'] = slot_id.role_id.vehicle_id.tag_id
        return res

    def convert_lead_to_quotation(self, crm_id=False, role_id=False):
        order_id = super(AutoPlanningWizard, self).convert_lead_to_quotation(crm_id, role_id)
        if not crm_id and not role_id:
            order_id['referrer_id'] = self.planning_ids.filtered(lambda x: x.is_selected)[
                0].mapped('role_id').vehicle_id.driver_id.id
        return order_id


class AutoPlanningLineWizard(models.TransientModel):
    _inherit = 'auto.planning.line.wizard'

    tag_id = fields.Many2one('fleet.vehicle.tag', string="Type vehicle")
