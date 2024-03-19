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
from collections import OrderedDict

import phonenumbers
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools import config
from datetime import datetime, timedelta

import json

# Get server timezone
TZ = (time.timezone / 60 / 60) if time.timezone != 0 else -3
MARGIN = 3600
_logger = logging.Logger(__name__)

def check_int_in_list_of_dicts(list_of_dicts, key, value):

    for dictionary in list_of_dicts:
        if key in dictionary and dictionary[key].id == value:
            return True
    return False

def get_value_by_search(list_of_dicts, search_key, search_value, target_key):
    for dictionary in list_of_dicts:
        if dictionary.get(search_key) == search_value:
            return dictionary.get(target_key)
    return None


def float_to_time(seconds):
    if not seconds: return "--:--:--"
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return formatted_time

class AutoPlanningWizard(models.TransientModel):
    _inherit = 'auto.planning.wizard'

    def get_mo_vehicle_recommandation(self, latlong_dict):
        middle_office_ids = self.env['middle.office'].get_default_recommandation()
        if  not middle_office_ids: 
            raise UserError(_("API recommandation not set !"))
        response = middle_office_ids.send_requests_to_mo(
            params=f"lat={latlong_dict.get('lat')}&lon={latlong_dict.get('lon')}",
            paramstypes="?",
            request="GET",
        )
        if response.status_code == 200:
            return response
        raise ValueError(_(
            'The request for get details failed'
        ))

    def get_role_by_immatricule(self, values):
        role = []
        vehicle_mo = self.get_mo_vehicle_recommandation(values)
        if vehicle_mo.text == '[]' : return role
        data_array = json.loads(vehicle_mo.text)
        for vehicle in data_array:
            if vehicle['status'] not in ['AVAILABLE','BUSY']:
                continue
            vehicle_id = self.env['planning.role'].sudo().search([('vehicle_id.license_plate','=',vehicle.get('immatriculation',''))],limit=1)
            dict_temp = {
                'vehicle_id': vehicle_id.id,
                'estimateDistance': vehicle['estimateDistance'],
                'estimateTimeofArrival': vehicle['estimateTimeofArrival'],
                'status': vehicle['status']
            }
            if vehicle_id: role.append(dict_temp)
        return role

    @api.model
    def default_get(self, fields):
        planning = super(AutoPlanningWizard, self).default_get(fields)
        record_id = self.env['crm.lead'].sudo().browse(self._context.get('active_ids'))
        role_mo_service = self.get_role_by_immatricule({
            "lat": record_id.pick_up_lat,
            "lon": record_id.pick_up_long
        })
        planning_array = planning['planning_ids']
        for array in planning_array:
            if array[2]:
                role_id = array[2].get('role_id', False)
                mo_state = get_value_by_search(role_mo_service, 'vehicle_id', role_id, 'status')
                array[2]['estimated_distance'] = get_value_by_search(role_mo_service, 'vehicle_id', role_id, 'estimateDistance')
                array[2]['estimated_time_arrival'] = float_to_time(get_value_by_search(role_mo_service, 'vehicle_id', role_id, 'estimateTimeofArrival'))
                array[2]['mo_state'] = mo_state
        planning['planning_ids'] = sorted(planning_array, key=lambda x: (
            x[2].get('estimated_time_arrival', "--:--:--") == "--:--:--",
            x[2].get('estimated_time_arrival', "--:--:--")
        ))
        return planning


class AutoPlanningLineWizard(models.TransientModel):
    _inherit = 'auto.planning.line.wizard'


    mo_state = fields.Char("Middle Office state")
    estimated_distance = fields.Float('Estimated distance to join')
    estimated_time_arrival = fields.Char('Estimated time to join')