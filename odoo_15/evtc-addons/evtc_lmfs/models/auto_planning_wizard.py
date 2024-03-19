# -*- coding: utf-8 -*-
import json
from odoo import _, models
from odoo.exceptions import ValidationError

class AutoPlanningWizard(models.TransientModel):
    _inherit = 'auto.planning.wizard'

    def validate(self):
        result = super(AutoPlanningWizard, self).validate()
        opportunity_id = self.env['crm.lead'].sudo().browse(self._context.get('active_ids'))
        vehicles = opportunity_id.role_id.vehicle_id
        order_ids = opportunity_id.order_ids
        planning_id = self.planning_ids.filtered(lambda x: x.is_selected)[0]
        estimated_duration = 0
        estimated_distance = 0
        driver_name = ''
        if planning_id: 
            estimated_duration = planning_id.estimated_time_arrival
            estimated_distance = round(planning_id.estimated_distance,2)
            driver_name = self.driver_id.name

        driver_notes =  _(
            'Driver name: %s - Car details: %s with the license plate: %s'
        ) % (
            self.driver_id.name,
            str(planning_id.role_id.vehicle_id.model_id.name + " " + planning_id.role_id.vehicle_id.model_id.brand_id.name),
            planning_id.role_id.vehicle_id.license_plate,
        )
        order_ids[0].update({
            'order_line': [(0, 0, {
                            'display_type': 'line_section',
                            'name': driver_notes})],
        })
        if vehicles.geolocalization_type  == "lmfs" and not opportunity_id.is_location:
            mo_create_body = opportunity_id._prepare_locations()
            driver_contact = vehicles.driver_id.phone or vehicles.driver_id.mobile
            vehicles.create_mo_vehicle()
            if not driver_contact:
                raise  ValidationError(_('No contact found for driver of %s' % vehicles.name))
            if not order_ids:
                raise ValidationError(_('No order found for current opportunity'))
            mo_create_body.update({
                'driverPhone': driver_contact.replace(' ', ''),
                'immatriculationID': vehicles.license_plate,
                'dateCreated': opportunity_id.create_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if opportunity_id.create_date else '',
            })
            opportunity_id.formatted_json = json.dumps(mo_create_body)
            data_response = opportunity_id.create_mo_trip()
            if data_response:
                tasks = {}
                load_response = json.loads(data_response.content)
                opportunity_id.response_json = load_response
                for i, task in enumerate(load_response.get('taskInfos', [])):
                    key = {
                        'taskInfo': task.get('trackingId'),
                        'trackingIdShort': task.get('trackingIdShort', '')
                    }
                    tasks[i] = key
                opportunity_id.tracking = json.dumps(tasks)
                if tasks:
                    key_first = min(i for i in tasks)
                    opportunity_id.first_tracking = tasks[key_first]['taskInfo']
                    opportunity_id.tracking_id_short = tasks[key_first]['trackingIdShort']
        return result