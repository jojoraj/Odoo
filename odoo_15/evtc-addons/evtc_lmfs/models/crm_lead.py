# -*- coding: utf-8 -*-
import hashlib
import logging
import json
from datetime import datetime
from odoo import _, models, fields, api, SUPERUSER_ID

logger = logging.getLogger(__name__)

from odoo.addons.evtc_lmfs.services.data_request import compact_fields, fields_strip_values


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    siid = fields.Char(string='External MO ID')
    formatted_json = fields.Text(string='Json send to MO service', copy=False)
    response_json = fields.Text(string='Response', copy=False)
    vehicle_localization = fields.Selection(related="role_id.vehicle_id.geolocalization_type",
                                            string="Localisation type", copy=False)
    vehicle_type = fields.Char(related="role_id.vehicle_id.name", string="Vehicle Name", copy=False)
    tracking = fields.Text(string='Tracking IDs', copy=False)
    first_tracking = fields.Char('First tracking', copy=False)
    tracking_id_short = fields.Char('trackingIdShort', copy=False)
    vehicle_update_mo_response = fields.Char('Response on update vehicle', copy=False)
    mo_trip_id = fields.Char('Mo ID', copy=False)
    response_code = fields.Char('Response CODE', copy=False)

    step_request = fields.Text(copy=False)
    vehicle_request = fields.Text(copy=False)

    @staticmethod
    def sha256_hash_siid(hash):
        return hashlib.sha256(f'{fields.datetime.now()}-{hash}'.encode('utf-8')).hexdigest()


    def _hash_Siid(self):
        self.ensure_one()
        if not self.siid:
            self.siid = self.sha256_hash_siid(self.id)

    @api.model_create_multi
    def create(self, values):
        crm_id = super(CrmLead, self).create(values)
        if not crm_id.siid:
            crm_id.siid = self.sha256_hash_siid(self.id)
        return crm_id

    def _prepare_locations(self):
        trip_compact_data = compact_fields()
        locations = [fields_strip_values(self, trip_compact_data['pickup'])]
        if self.as_many_course:
            for record in self.others_destination:
                locations.append(
                    fields_strip_values(record, trip_compact_data['dest_with'])
                )
        elif not self.is_location:
            locations.append(fields_strip_values(self, trip_compact_data['dest_without']))
        body = trip_compact_data['trip_body']
        body['estimatedLength'] = self.estimated_kilometers
        body['estimatedPrice'] = int(''.join(filter(str.isdigit, self.estimated_price)))
        body['locations'] = locations
        body['siid'] = self.siid
        client = self.partner_id.phone or self.partner_id.mobile
        body['clientPhone'] = client.replace(' ', '') if client else None
        return body

    def create_mo_trip(self):
        data_mo = self.env['middle.office'].get_uri_trip()
        if data_mo:
            return data_mo.send_requests_to_mo(
                self.formatted_json, name=self._name
            )
        return False

    def get_opportunity_tracking(self):
        for record in self:
            if record.first_tracking:
                return record.first_tracking
        return str()

    def set_opportunity_request(self, values):
        collect_opp_errors = dict()
        stage = 'stage_id'
        for record in self:
            if stage in values:
                try:
                    stage_value = values[stage]
                    record[stage] = record.env.ref(stage_value).id
                except Exception as e:
                    collect_opp_errors[record._fields[stage].name] = str(e)
                    logger.warning(str(e))
        return collect_opp_errors

    role_has_down = fields.Boolean(related='role_id.vehicle_id.state_id.is_broken_down', domain=[('role_id','!=', False)])

    def get_step_xml_id(self):
        step = self.env.ref('evtc_lmfs.stage_pick_up_client')
        return step and step.id or None

    def get_end_xml_id(self):
        step = self.env.ref('evtc_lmfs.end_pickup_step')
        return step and step.id or None

    def get_abort_trip_xml_id(self):
        step = self.env.ref('esanandro_crm.stage_lead5')
        return step and step.id or None

    def get_start_trip_xml_id(self):
        step = self.env.ref('crm.stage_lead3')
        return step and step.id or None


    def update_mo_step(self, begin=False, end=False, start_trip=False, stop_trip=False, cancel_trip=False):
        step_conf = False
        middle_office = self.env['middle.office']
        if begin:
            step_conf = middle_office.get_uri_begin_step()
        if end:
            step_conf = middle_office.get_uri_end_step()
        if start_trip:
            step_conf = middle_office.get_uri_start_trip()
        if stop_trip:
            step_conf = middle_office.get_uri_stop_trip()
        if cancel_trip:
            step_conf = middle_office.get_uri_cancel_trip()
        if step_conf:
            return step_conf.send_requests_to_mo(payload=None, params=self.mo_trip_id)
        return False

    @api.model
    def progress_values(self, crm_lead_id):
        lead_id = self.browse(int(crm_lead_id)).exists()
        if lead_id:
            return lead_id.prepare_progress_values()
        return False

    course_b2b = fields.Boolean(String="Course B2B", default=False)

    def write(self, values):
        current_stage = values.get('stage_id')
        super().write(values)
        self._hash_Siid()
        orders = self.order_ids.filtered(lambda s: s.state == 'draft')
        order_id = orders[-1] if len(orders) > 1 else orders
        if self.role_id.vehicle_id.geolocalization_type == 'geotab':
            if current_stage and current_stage == self.get_step_xml_id():
                self.update_mo_step(begin=True)
            if current_stage and current_stage == self.get_end_xml_id():
                self.update_mo_step(end=True)
            if current_stage and current_stage == self.get_start_trip_xml_id():
                self.update_mo_step(start_trip=True)
            if self.stage_id == self.env.ref('crm.stage_lead3') and order_id:
                order_id.start_course_geotab_vehicle()
            if self.stage_id == self.env.ref('esanandro_crm.stage_lead6'):
                if order_id:
                    order_id.end_course_geotab_vehicle()
                self.update_mo_step(stop_trip=True)
        if current_stage and current_stage == self.get_abort_trip_xml_id():
            self.update_mo_step(cancel_trip=True)
        
        if self.course_b2b and order_id:
            if self.partner_id.is_b2b and self.partner_id.related_company:
                order_id.update({
                    'partner_id': self.partner_id.related_company.id
                })
        if not self.course_b2b and order_id: 
            order_id.update({
                    'partner_id': self.partner_id.id
                })

    @api.model
    def get_crm_stage(self):
        return {
            'new_request': self.env.ref('crm.stage_lead1'),
            'trip_confirmed': self.env.ref('esanandro_crm.stage_lead7'),
            'trip_affected': self.env.ref('crm.stage_lead2'),
            'driver_coming': self.env.ref('evtc_lmfs.stage_pick_up_client'),
            'end_pick_up_client': self.env.ref('evtc_lmfs.end_pickup_step'),
            'in_progress': self.env.ref('crm.stage_lead3'),
            'compta': self.env.ref('crm.stage_lead4'),
            'terminated': self.env.ref('esanandro_crm.stage_lead6'),
            'refused': self.env.ref('esanandro_crm.stage_lead5'),
        }   



    def prepare_progress_values(self):
        crm_stage = self.get_crm_stage()
        values = {}
        progressions = [
            ('50', '0', '0'),('75','0','0'),('100','0','0'),
            ('100', '25', '0'),('100', '50', '0'),('100', '100', '0'),
            ('100', '100', '100'),('0', '0', '0')
        ]
        stages = {
            crm_stage['new_request']: (_('Request being validated'), 1, 'step-one', progressions[0]),
            crm_stage['trip_confirmed']: (_('Your trip is confirm'), 2, 'step-two', progressions[1]),
            crm_stage['trip_affected']: (_('Your trip is affected'), 10, 'step-three', progressions[2]),
            crm_stage['driver_coming']: (_('Your driver is on his way'), 3, 'step-three', progressions[3]),
            crm_stage['end_pick_up_client']: (_('You have been picked up'), 3, 'step-three', progressions[4]),
            crm_stage['in_progress']: (_("trip in progress"), 4, 'step-four', progressions[5]),
            crm_stage['compta']: (_("trip finish"), 4, 'step-four', progressions[6]),
            crm_stage['terminated']: (self.stage_id.name, 4, 'step-four', progressions[6]),
            crm_stage['refused']: (_('The race is refused'), 3, 'step-three', progressions[7])
        }
        if self.stage_id in stages:
            state_label, step, class_step, progression = stages[self.stage_id]
            values.update({
                'state_label': state_label,
                'step': step,
                'class_step': class_step,
                'progression': progression
            })
        else:
            values.update({
                'state_label': 'Unknown step',
                'step': 1,
                'class_step': 'step-one',
                'progression': progressions[0]
            })
        return values

    def get_opportunity_tracking(self):
        for record in self:
            if record.first_tracking:
                return record.first_tracking
        return str()


  